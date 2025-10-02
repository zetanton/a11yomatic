import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { analysisAPI, remediationAPI, reportsAPI } from '../../services/api';

const AnalysisResults: React.FC = () => {
  const { pdfId } = useParams<{ pdfId: string }>();
  const [selectedIssue, setSelectedIssue] = useState<any>(null);
  const [remediation, setRemediation] = useState<any>(null);

  const { data: analysis, isLoading, refetch } = useQuery({
    queryKey: ['analysis', pdfId],
    queryFn: async () => {
      const response = await analysisAPI.getResults(pdfId!);
      return response.data;
    },
    enabled: !!pdfId,
    refetchInterval: (data) => {
      // Keep polling if status is processing
      return data?.status === 'processing' ? 3000 : false;
    },
  });

  const { data: report } = useQuery({
    queryKey: ['report', pdfId],
    queryFn: async () => {
      const response = await reportsAPI.get(pdfId!);
      return response.data;
    },
    enabled: !!pdfId && analysis?.status === 'completed',
  });

  const getSeverityBadge = (severity: string) => {
    const classes = {
      critical: 'badge-critical',
      high: 'badge-high',
      medium: 'badge-medium',
      low: 'badge-low',
    };
    return classes[severity as keyof typeof classes] || 'badge';
  };

  const handleGenerateRemediation = async (issueId: string) => {
    try {
      const response = await remediationAPI.generate(issueId);
      setRemediation(response.data);
    } catch (error) {
      console.error('Failed to generate remediation:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        <p className="text-gray-400 mt-4">Loading analysis...</p>
      </div>
    );
  }

  if (analysis?.status === 'processing') {
    return (
      <div className="text-center py-12 card">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500"></div>
        <h2 className="text-2xl font-semibold mt-6 mb-2">Analyzing PDF...</h2>
        <p className="text-gray-400">
          This may take a few moments. We're checking for accessibility issues.
        </p>
      </div>
    );
  }

  if (!analysis || analysis.status === 'failed') {
    return (
      <div className="text-center py-12 card">
        <h2 className="text-2xl font-semibold text-red-500 mb-4">
          Analysis Failed
        </h2>
        <p className="text-gray-400">
          There was an error analyzing your PDF. Please try uploading it again.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Analysis Results</h1>
        <p className="text-gray-400 mt-2">
          Review accessibility issues and remediation suggestions
        </p>
      </div>

      {/* Summary Cards */}
      {report && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="card">
            <div className="text-sm text-gray-400">Overall Score</div>
            <div className="text-3xl font-bold text-primary-500 mt-2">
              {report.overall_score}/100
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Total Issues</div>
            <div className="text-3xl font-bold text-orange-500 mt-2">
              {report.total_issues}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Critical</div>
            <div className="text-3xl font-bold text-red-500 mt-2">
              {report.critical_issues}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">High</div>
            <div className="text-3xl font-bold text-orange-400 mt-2">
              {report.high_issues}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Medium/Low</div>
            <div className="text-3xl font-bold text-yellow-500 mt-2">
              {report.medium_issues + report.low_issues}
            </div>
          </div>
        </div>
      )}

      {/* Issues List */}
      <div className="card">
        <h2 className="text-2xl font-semibold mb-6">Accessibility Issues</h2>

        {analysis.issues && analysis.issues.length > 0 ? (
          <div className="space-y-4">
            {analysis.issues.map((issue: any) => (
              <div
                key={issue.id}
                className="border border-dark-700 rounded-lg p-4 hover:border-primary-500 transition-colors cursor-pointer"
                onClick={() => setSelectedIssue(issue)}
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center space-x-3 mb-2">
                      <span className={`${getSeverityBadge(issue.severity)}`}>
                        {issue.severity}
                      </span>
                      <span className="text-sm text-gray-400">
                        {issue.page_number && `Page ${issue.page_number}`}
                      </span>
                      {issue.wcag_criteria && (
                        <span className="text-sm text-gray-400">
                          WCAG {issue.wcag_criteria}
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-medium mb-2">
                      {issue.issue_type.replace(/_/g, ' ').toUpperCase()}
                    </h3>
                    <p className="text-gray-400 text-sm">{issue.description}</p>
                  </div>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleGenerateRemediation(issue.id);
                    }}
                    className="btn-primary text-sm ml-4"
                  >
                    Generate Fix
                  </button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-400">No accessibility issues found!</p>
            <p className="text-green-500 mt-2">Your PDF looks great!</p>
          </div>
        )}
      </div>

      {/* Remediation Modal */}
      {remediation && (
        <div className="fixed inset-0 bg-black bg-opacity-75 flex items-center justify-center p-4 z-50">
          <div className="card max-w-2xl w-full">
            <h3 className="text-xl font-semibold mb-4">
              AI-Generated Remediation Suggestion
            </h3>
            <div className="bg-dark-700 rounded-lg p-4 mb-6">
              <p className="text-gray-300 whitespace-pre-wrap">
                {remediation.ai_generated_content}
              </p>
            </div>
            <div className="flex justify-end space-x-4">
              <button
                onClick={() => setRemediation(null)}
                className="btn-secondary"
              >
                Close
              </button>
              <button
                onClick={() => {
                  // Handle approval
                  remediationAPI.approve(remediation.issue_id, true);
                  setRemediation(null);
                }}
                className="btn-primary"
              >
                Approve & Apply
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AnalysisResults;


