import React from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import apiService from '../../services/api';

const AnalysisResults: React.FC = () => {
  const { pdfId } = useParams<{ pdfId: string }>();
  const navigate = useNavigate();

  const { data: analysis, isLoading, error } = useQuery({
    queryKey: ['analysis', pdfId],
    queryFn: () => apiService.getAnalysis(pdfId!),
    enabled: !!pdfId,
  });

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'bg-red-900/20 text-red-400 border-red-500';
      case 'high':
        return 'bg-orange-900/20 text-orange-400 border-orange-500';
      case 'medium':
        return 'bg-yellow-900/20 text-yellow-400 border-yellow-500';
      case 'low':
        return 'bg-blue-900/20 text-blue-400 border-blue-500';
      default:
        return 'bg-gray-900/20 text-gray-400 border-gray-500';
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400">Loading analysis...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">Failed to load analysis</p>
        </div>
        <button onClick={() => navigate('/pdfs')} className="mt-4 btn btn-secondary">
          Back to PDFs
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Accessibility Analysis</h1>
        <button onClick={() => navigate('/pdfs')} className="btn btn-secondary">
          Back to PDFs
        </button>
      </div>

      {/* Score Card */}
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-white mb-2">Overall Score</h2>
            <p className="text-gray-400">
              WCAG Compliance: {analysis?.wcag_compliance_level}
            </p>
          </div>
          <div className="text-right">
            <div className="text-5xl font-bold text-primary-500">
              {analysis?.overall_score}/100
            </div>
          </div>
        </div>
      </div>

      {/* Issue Summary */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="card border-l-4 border-red-500">
          <h3 className="text-sm font-medium text-gray-400">Critical Issues</h3>
          <p className="mt-2 text-3xl font-bold text-red-500">
            {analysis?.critical_issues || 0}
          </p>
        </div>
        <div className="card border-l-4 border-orange-500">
          <h3 className="text-sm font-medium text-gray-400">High Priority</h3>
          <p className="mt-2 text-3xl font-bold text-orange-500">
            {analysis?.high_issues || 0}
          </p>
        </div>
        <div className="card border-l-4 border-yellow-500">
          <h3 className="text-sm font-medium text-gray-400">Medium Priority</h3>
          <p className="mt-2 text-3xl font-bold text-yellow-500">
            {analysis?.medium_issues || 0}
          </p>
        </div>
        <div className="card border-l-4 border-blue-500">
          <h3 className="text-sm font-medium text-gray-400">Low Priority</h3>
          <p className="mt-2 text-3xl font-bold text-blue-500">
            {analysis?.low_issues || 0}
          </p>
        </div>
      </div>

      {/* Issues List */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-bold text-white">
            Accessibility Issues ({analysis?.total_issues || 0})
          </h2>
          <button className="btn btn-primary">Generate Remediation</button>
        </div>

        <div className="space-y-4">
          {analysis?.issues?.map((issue: any) => (
            <div
              key={issue.id}
              className={`p-4 rounded-lg border ${getSeverityColor(issue.severity)}`}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-2">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded text-xs font-medium capitalize">
                      {issue.severity}
                    </span>
                    <span className="text-xs text-gray-400">
                      WCAG {issue.wcag_criteria}
                    </span>
                    {issue.page_number && (
                      <span className="text-xs text-gray-400">
                        Page {issue.page_number}
                      </span>
                    )}
                  </div>
                  <h3 className="mt-2 text-base font-medium capitalize">
                    {issue.issue_type.replace(/_/g, ' ')}
                  </h3>
                  <p className="mt-1 text-sm text-gray-300">
                    {issue.description}
                  </p>
                </div>
                <button className="ml-4 btn btn-secondary">
                  Fix Issue
                </button>
              </div>
            </div>
          ))}
        </div>

        {(!analysis?.issues || analysis.issues.length === 0) && (
          <div className="text-center py-8">
            <div className="text-gray-400">No accessibility issues found!</div>
            <p className="mt-2 text-green-400">
              This document appears to be fully accessible.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisResults;
