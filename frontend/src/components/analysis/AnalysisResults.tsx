import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { analysisAPI, remediationAPI, reportsAPI, pdfAPI } from '../../services/api';

const AnalysisResults: React.FC = () => {
  const { pdfId } = useParams<{ pdfId: string }>();
  const [selectedIssue, setSelectedIssue] = useState<any>(null);
  const [remediation, setRemediation] = useState<any>(null);
  const [fixedIssues, setFixedIssues] = useState<Set<string>>(new Set());
  const [fixingIssues, setFixingIssues] = useState<Set<string>>(new Set());
  const [isApplyingAll, setIsApplyingAll] = useState(false);

  const { data: analysis, isLoading, refetch } = useQuery({
    queryKey: ['analysis', pdfId],
    queryFn: async () => {
      const response = await analysisAPI.getResults(pdfId!);
      return response.data;
    },
    enabled: !!pdfId,
    refetchInterval: (data: any) => {
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

  const handleApplyFix = async (issueId: string) => {
    setFixingIssues(prev => new Set(prev).add(issueId));
    
    try {
      // Generate and apply remediation
      await remediationAPI.generate(issueId);
      await remediationAPI.approve(issueId, true);
      
      setFixedIssues(prev => new Set(prev).add(issueId));
      
      // Refresh analysis to show updated status
      setTimeout(() => refetch(), 500);
    } catch (error) {
      console.error('Failed to apply fix:', error);
      alert('Failed to apply fix. Please try again.');
    } finally {
      setFixingIssues(prev => {
        const newSet = new Set(prev);
        newSet.delete(issueId);
        return newSet;
      });
    }
  };

  const handleApplyAllFixes = async () => {
    if (!analysis?.issues || analysis.issues.length === 0) return;
    
    const confirmed = window.confirm(
      `Apply automatic fixes to all ${analysis.issues.length} issues? This will modify the PDF.`
    );
    
    if (!confirmed) return;
    
    setIsApplyingAll(true);
    
    try {
      // Use bulk remediation endpoint
      const response = await remediationAPI.bulkRemediatePdf(pdfId!);
      
      // Mark all issues as fixed
      const allIssueIds = analysis.issues.map((issue: any) => issue.id);
      setFixedIssues(new Set(allIssueIds));
      
      alert(`All fixes applied successfully!\n\n${response.data.count} issues fixed.\n\nClick "Download Fixed PDF" to get your accessible document.`);
      refetch();
    } catch (error) {
      console.error('Failed to apply all fixes:', error);
      alert('Failed to apply all fixes. Please try again or fix issues individually.');
    } finally {
      setIsApplyingAll(false);
    }
  };

  const handleDownloadFixed = async () => {
    try {
      const response = await pdfAPI.downloadFixed(pdfId!);
      
      // Create blob URL and trigger download
      const blob = new Blob([response.data], { type: 'application/pdf' });
      const url = window.URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `fixed_${pdfId}.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download fixed PDF:', error);
      alert('Failed to download fixed PDF. Please try again.');
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-maroon"></div>
        <p className="text-gray-600 mt-4">Loading analysis...</p>
      </div>
    );
  }

  if (analysis?.status === 'processing') {
    return (
      <div className="text-center py-12 card">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-maroon"></div>
        <h2 className="text-2xl font-semibold mt-6 mb-2">Analyzing PDF...</h2>
        <p className="text-gray-600">
          This may take a few moments. We're checking for accessibility issues.
        </p>
      </div>
    );
  }

  if (!analysis || analysis.status === 'failed') {
    return (
      <div className="text-center py-12 card">
        <h2 className="text-2xl font-semibold text-red-600 mb-4">
          Analysis Failed
        </h2>
        <p className="text-gray-600">
          There was an error analyzing your PDF. Please try uploading it again.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <h1 className="text-3xl font-bold">Analysis Results</h1>
          <p className="text-gray-600 mt-2">
            Review and fix accessibility issues
          </p>
        </div>
        <div className="flex gap-3">
          {fixedIssues.size > 0 && (
            <button
              onClick={handleDownloadFixed}
              className="btn-primary"
            >
              📥 Download Fixed PDF
            </button>
          )}
          {analysis?.issues && analysis.issues.length > 0 && (
            <button
              onClick={handleApplyAllFixes}
              disabled={isApplyingAll || fixedIssues.size === analysis.issues.length}
              className="btn-secondary"
            >
              {isApplyingAll ? '⚙️ Applying Fixes...' : '🔧 Fix All Issues'}
            </button>
          )}
        </div>
      </div>

      {/* Summary Cards */}
      {report && (
        <div className="grid grid-cols-1 md:grid-cols-5 gap-6">
          <div className="card">
            <div className="text-sm text-gray-400">Overall Score</div>
            <div className="text-3xl font-bold text-maroon mt-2">
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
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold">Accessibility Issues</h2>
          {analysis?.issues && analysis.issues.length > 0 && (
            <div className="text-sm">
              <span className="text-gray-600">Fixed: </span>
              <span className="font-bold text-green-600">{fixedIssues.size}</span>
              <span className="text-gray-400"> / </span>
              <span className="font-bold text-gray-900">{analysis.issues.length}</span>
              <div className="w-48 bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-green-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${(fixedIssues.size / analysis.issues.length) * 100}%` }}
                />
              </div>
            </div>
          )}
        </div>

        {analysis.issues && analysis.issues.length > 0 ? (
          <div className="space-y-4">
            {analysis.issues.map((issue: any) => (
              <div
                key={issue.id}
                className={`border rounded-lg p-4 transition-all ${
                  fixedIssues.has(issue.id) 
                    ? 'border-green-300 bg-green-50' 
                    : 'border-gray-200 bg-white hover:border-maroon hover:shadow-md'
                }`}
              >
                <div className="flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-2 flex-wrap">
                      {fixedIssues.has(issue.id) && (
                        <span className="badge bg-green-100 text-green-800 border-green-300">
                          ✓ Fixed
                        </span>
                      )}
                      <span className={`${getSeverityBadge(issue.severity)}`}>
                        {issue.severity}
                      </span>
                      <span className="text-sm text-gray-600">
                        {issue.page_number && `Page ${issue.page_number}`}
                      </span>
                      {issue.wcag_criteria && (
                        <span className="text-sm text-gray-600">
                          WCAG {issue.wcag_criteria}
                        </span>
                      )}
                    </div>
                    <h3 className="text-lg font-medium mb-2">
                      {issue.issue_type.replace(/_/g, ' ').toUpperCase()}
                    </h3>
                    <p className="text-gray-600 text-sm mb-3">{issue.description}</p>
                    
                    {/* Quick Fix Description */}
                    <div className="text-xs bg-blue-50 border border-blue-200 rounded-lg p-3 inline-block">
                      <p className="font-semibold text-blue-900 mb-1">Quick Fix:</p>
                      <p className="text-blue-800">
                        {issue.issue_type === 'missing_alt_text' && 'Add descriptive alt text to images'}
                        {issue.issue_type === 'heading_structure' && 'Fix heading hierarchy (H1→H2→H3)'}
                        {issue.issue_type === 'color_contrast' && 'Increase color contrast ratio to 4.5:1'}
                        {issue.issue_type === 'table_structure' && 'Add table headers and row/column labels'}
                        {issue.issue_type === 'reading_order' && 'Reorder content for logical flow'}
                        {issue.issue_type === 'form_labels' && 'Add labels to all form fields'}
                        {issue.issue_type === 'link_text' && 'Use descriptive link text (not "click here")'}
                        {!['missing_alt_text', 'heading_structure', 'color_contrast', 'table_structure', 'reading_order', 'form_labels', 'link_text'].includes(issue.issue_type) && 'Review and apply accessibility standards'}
                      </p>
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <div className="flex-shrink-0">
                    {fixedIssues.has(issue.id) ? (
                      <div className="text-center">
                        <div className="text-green-600 text-3xl mb-1">✓</div>
                        <p className="text-xs text-green-700 font-medium">Applied</p>
                      </div>
                    ) : (
                      <button
                        onClick={() => handleApplyFix(issue.id)}
                        disabled={fixingIssues.has(issue.id)}
                        className="btn-primary text-sm whitespace-nowrap"
                      >
                        {fixingIssues.has(issue.id) ? '⚙️ Fixing...' : '🔧 Apply Fix'}
                      </button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8">
            <p className="text-gray-600">No accessibility issues found!</p>
            <p className="text-green-600 mt-2">Your PDF looks great!</p>
          </div>
        )}
      </div>

      {/* Remediation Modal */}
      {remediation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="card max-w-2xl w-full">
            <h3 className="text-xl font-semibold mb-4">
              AI-Generated Remediation Suggestion
            </h3>
            <div className="bg-gray-50 rounded-lg p-4 mb-6 border border-gray-200">
              <p className="text-gray-700 whitespace-pre-wrap">
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


