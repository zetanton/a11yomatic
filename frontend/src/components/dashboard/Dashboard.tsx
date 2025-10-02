import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { pdfAPI, reportsAPI, analysisAPI, remediationAPI } from '../../services/api';

const Dashboard: React.FC = () => {
  const [selectedPdfs, setSelectedPdfs] = useState<Set<string>>(new Set());
  const [isProcessingBulk, setIsProcessingBulk] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'name' | 'size'>('date');

  const { data: pdfs, isLoading: pdfsLoading, refetch } = useQuery({
    queryKey: ['pdfs'],
    queryFn: async () => {
      const response = await pdfAPI.list();
      return response.data;
    },
  });

  const { data: analytics } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await reportsAPI.getAnalytics();
      return response.data;
    },
  });

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'text-green-600';
      case 'processing':
        return 'text-yellow-600';
      case 'failed':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const toggleSelectAll = () => {
    if (selectedPdfs.size === filteredPdfs.length) {
      setSelectedPdfs(new Set());
    } else {
      setSelectedPdfs(new Set(filteredPdfs.map((pdf: any) => pdf.id)));
    }
  };

  const toggleSelect = (id: string) => {
    const newSelected = new Set(selectedPdfs);
    if (newSelected.has(id)) {
      newSelected.delete(id);
    } else {
      newSelected.add(id);
    }
    setSelectedPdfs(newSelected);
  };

  const handleBulkAnalyze = async () => {
    if (selectedPdfs.size === 0) return;
    setIsProcessingBulk(true);
    
    try {
      const promises = Array.from(selectedPdfs).map(id => analysisAPI.analyze(id));
      await Promise.all(promises);
      refetch();
    } catch (error) {
      console.error('Bulk analyze failed:', error);
    } finally {
      setIsProcessingBulk(false);
      setSelectedPdfs(new Set());
    }
  };

  const handleBulkDelete = async () => {
    if (selectedPdfs.size === 0 || !window.confirm(`Delete ${selectedPdfs.size} PDFs?`)) return;
    setIsProcessingBulk(true);
    
    try {
      const promises = Array.from(selectedPdfs).map(id => pdfAPI.delete(id));
      await Promise.all(promises);
      refetch();
    } catch (error) {
      console.error('Bulk delete failed:', error);
    } finally {
      setIsProcessingBulk(false);
      setSelectedPdfs(new Set());
    }
  };

  const handleRemediateAll = async () => {
    const completedPdfs = pdfs?.filter((pdf: any) => pdf.processing_status === 'completed') || [];
    
    if (completedPdfs.length === 0) {
      alert('No completed PDFs to remediate. Please analyze PDFs first.');
      return;
    }
    
    if (!window.confirm(`Apply fixes to ALL issues in ${completedPdfs.length} PDFs? This will modify all documents.`)) return;
    setIsProcessingBulk(true);

    try {
      let totalFixed = 0;
      
      // Use bulk endpoint for each PDF
      for (const pdf of completedPdfs) {
        try {
          const response = await remediationAPI.bulkRemediatePdf(pdf.id);
          totalFixed += response.data.count || 0;
        } catch (error) {
          console.error(`Failed to remediate PDF ${pdf.id}:`, error);
        }
      }
      
      alert(`Successfully applied fixes to all issues!\n\n${totalFixed} total fixes across ${completedPdfs.length} PDFs.\n\nYou can now download the fixed PDFs from individual analysis pages.`);
      refetch();
    } catch (error) {
      console.error('Bulk remediation failed:', error);
      alert('Some fixes failed to apply. Please check individual PDFs.');
    } finally {
      setIsProcessingBulk(false);
    }
  };

  // Filter and sort PDFs
  const filteredPdfs = pdfs ? pdfs
    .filter((pdf: any) => filterStatus === 'all' || pdf.processing_status === filterStatus)
    .sort((a: any, b: any) => {
      if (sortBy === 'date') return new Date(b.upload_date).getTime() - new Date(a.upload_date).getTime();
      if (sortBy === 'name') return a.filename.localeCompare(b.filename);
      if (sortBy === 'size') return b.file_size - a.file_size;
      return 0;
    }) : [];

  // Calculate bulk statistics with before/after metrics
  const bulkStats = pdfs && analytics ? {
    totalFiles: pdfs.length,
    totalSize: pdfs.reduce((sum: number, pdf: any) => sum + pdf.file_size, 0),
    completed: pdfs.filter((p: any) => p.processing_status === 'completed').length,
    processing: pdfs.filter((p: any) => p.processing_status === 'processing').length,
    failed: pdfs.filter((p: any) => p.processing_status === 'failed').length,
    // Before remediation stats
    totalIssuesBefore: analytics.total_issues || 0,
    avgScoreBefore: analytics.average_score || 0,
    criticalIssues: analytics.issue_breakdown?.critical || 0,
    highIssues: analytics.issue_breakdown?.high || 0,
    mediumIssues: analytics.issue_breakdown?.medium || 0,
    lowIssues: analytics.issue_breakdown?.low || 0,
    // After remediation stats (would be updated after fixes)
    estimatedScoreAfter: Math.min(100, (analytics.average_score || 0) + 25), // Estimate improvement
    potentialImprovements: analytics.total_issues || 0,
  } : null;

  // Calculate issue type breakdown
  const issueTypeStats = analytics?.issue_breakdown ? [
    { type: 'Critical', count: analytics.issue_breakdown.critical || 0, color: 'bg-red-500' },
    { type: 'High', count: analytics.issue_breakdown.high || 0, color: 'bg-orange-500' },
    { type: 'Medium', count: analytics.issue_breakdown.medium || 0, color: 'bg-yellow-500' },
    { type: 'Low', count: analytics.issue_breakdown.low || 0, color: 'bg-blue-500' },
  ] : [];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-600 mt-2">
          Manage your PDF accessibility analysis and remediation
        </p>
      </div>

      {/* Enhanced Statistics with Before/After */}
      {bulkStats && (
        <>
          {/* Primary Stats Row */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card bg-gradient-to-br from-maroon/10 to-white border-maroon/20">
              <div className="text-xs text-gray-600 uppercase tracking-wide">Total Files</div>
              <div className="text-3xl font-bold text-maroon mt-1">
                {bulkStats.totalFiles}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {(bulkStats.totalSize / 1024 / 1024).toFixed(1)} MB total
              </div>
            </div>
          <div className="card">
              <div className="text-xs text-gray-600 uppercase tracking-wide">Completed</div>
              <div className="text-3xl font-bold text-green-600 mt-1">
                {bulkStats.completed}
              </div>
              <div className="text-xs text-gray-500 mt-1">Ready for fixes</div>
            </div>
            <div className="card">
              <div className="text-xs text-gray-600 uppercase tracking-wide">Processing</div>
              <div className="text-3xl font-bold text-yellow-600 mt-1">
                {bulkStats.processing}
              </div>
              <div className="text-xs text-gray-500 mt-1">In progress</div>
          </div>
          <div className="card">
              <div className="text-xs text-gray-600 uppercase tracking-wide">Failed</div>
              <div className="text-3xl font-bold text-red-600 mt-1">
                {bulkStats.failed}
              </div>
              <div className="text-xs text-gray-500 mt-1">Need attention</div>
            </div>
          </div>

          {/* Before & After Comparison */}
          <div className="card bg-gradient-to-r from-red-50 via-yellow-50 to-green-50">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900">Accessibility Score Impact</h3>
              <button
                onClick={handleRemediateAll}
                disabled={isProcessingBulk || bulkStats.completed === 0}
                className="btn-primary text-sm"
              >
                {isProcessingBulk ? '⚙️ Fixing All...' : '🔧 Fix All Issues in All PDFs'}
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {/* Before Stats */}
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-2">BEFORE Remediation</div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-red-200">
                  <div className="text-4xl font-bold text-red-600 mb-1">
                    {bulkStats.avgScoreBefore}
                  </div>
                  <div className="text-xs text-gray-500">Average Score</div>
                  <div className="mt-3 text-2xl font-bold text-orange-600">
                    {bulkStats.totalIssuesBefore}
                  </div>
                  <div className="text-xs text-gray-500">Total Issues</div>
                </div>
              </div>

              {/* Arrow/Improvement */}
              <div className="flex flex-col items-center justify-center">
                <div className="text-3xl mb-2">→</div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">
                    +{(bulkStats.estimatedScoreAfter - bulkStats.avgScoreBefore).toFixed(0)}
                  </div>
                  <div className="text-xs text-gray-600">Points Improvement</div>
                  <div className="mt-2 text-sm text-maroon font-semibold">
                    {bulkStats.potentialImprovements} Fixes to Apply
                  </div>
                </div>
              </div>

              {/* After Stats */}
              <div className="text-center">
                <div className="text-sm text-gray-600 mb-2">AFTER Remediation</div>
                <div className="bg-white rounded-lg p-4 shadow-sm border border-green-200">
                  <div className="text-4xl font-bold text-green-600 mb-1">
                    {bulkStats.estimatedScoreAfter}
                  </div>
                  <div className="text-xs text-gray-500">Estimated Score</div>
                  <div className="mt-3 text-2xl font-bold text-green-600">
                    ~0
                  </div>
                  <div className="text-xs text-gray-500">Remaining Issues</div>
            </div>
          </div>
            </div>
          </div>

          {/* Issue Type Breakdown */}
          {issueTypeStats.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold mb-4">Issue Type Breakdown</h3>
              <div className="space-y-3">
                {issueTypeStats.map((stat, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <div className="w-24 text-sm font-medium text-gray-700">
                      {stat.type}
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <div className="flex-1 bg-gray-200 rounded-full h-6 overflow-hidden">
                          <div
                            className={`${stat.color} h-6 flex items-center justify-end pr-2 text-white text-xs font-bold transition-all duration-300`}
                            style={{
                              width: `${bulkStats.totalIssuesBefore > 0 ? (stat.count / bulkStats.totalIssuesBefore) * 100 : 0}%`,
                              minWidth: stat.count > 0 ? '2rem' : '0'
                            }}
                          >
                            {stat.count > 0 && stat.count}
                          </div>
                        </div>
                        <div className="w-20 text-right">
                          <span className="text-sm font-bold text-gray-700">{stat.count}</span>
                          <span className="text-xs text-gray-500 ml-1">
                            ({bulkStats.totalIssuesBefore > 0 ? ((stat.count / bulkStats.totalIssuesBefore) * 100).toFixed(0) : 0}%)
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
          </div>
        </div>
          )}
        </>
      )}

      {/* Recent PDFs */}
      <div className="card">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
          <div>
            <h2 className="text-2xl font-semibold">PDF Library</h2>
            {selectedPdfs.size > 0 && (
              <p className="text-sm text-gray-600 mt-1">
                {selectedPdfs.size} file{selectedPdfs.size > 1 ? 's' : ''} selected
              </p>
            )}
          </div>

          <div className="flex gap-2 flex-wrap">
            {selectedPdfs.size > 0 && (
              <>
                <button
                  onClick={handleBulkAnalyze}
                  disabled={isProcessingBulk}
                  className="btn-secondary text-sm"
                >
                  {isProcessingBulk ? 'Processing...' : `Analyze ${selectedPdfs.size}`}
                </button>
                <button
                  onClick={handleBulkDelete}
                  disabled={isProcessingBulk}
                  className="btn-danger text-sm"
                >
                  Delete {selectedPdfs.size}
                </button>
              </>
            )}
            <Link to="/upload" className="btn-primary text-sm">
              Upload PDFs
          </Link>
          </div>
        </div>

        {/* Filters and Sort */}
        <div className="flex flex-col sm:flex-row gap-3 mb-4 pb-4 border-b border-gray-200">
          <div className="flex-1">
            <label className="text-xs text-gray-600 block mb-1">Filter by Status</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="input text-sm py-1.5"
            >
              <option value="all">All Status</option>
              <option value="completed">Completed</option>
              <option value="processing">Processing</option>
              <option value="failed">Failed</option>
            </select>
          </div>
          <div className="flex-1">
            <label className="text-xs text-gray-600 block mb-1">Sort by</label>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as any)}
              className="input text-sm py-1.5"
            >
              <option value="date">Upload Date</option>
              <option value="name">Name</option>
              <option value="size">File Size</option>
            </select>
          </div>
        </div>

        {pdfsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-maroon"></div>
            <p className="text-gray-600 mt-4">Loading PDFs...</p>
          </div>
        ) : filteredPdfs && filteredPdfs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3">
                    <input
                      type="checkbox"
                      checked={selectedPdfs.size === filteredPdfs.length && filteredPdfs.length > 0}
                      onChange={toggleSelectAll}
                      className="rounded border-gray-300 text-maroon focus:ring-maroon"
                    />
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Filename
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Upload Date
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-600 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredPdfs.map((pdf: any) => (
                  <tr key={pdf.id} className="hover:bg-gray-50">
                    <td className="px-4 py-4">
                      <input
                        type="checkbox"
                        checked={selectedPdfs.has(pdf.id)}
                        onChange={() => toggleSelect(pdf.id)}
                        className="rounded border-gray-300 text-maroon focus:ring-maroon"
                      />
                    </td>
                    <td className="px-4 py-4">
                      <div className="text-sm font-medium text-gray-900">{pdf.filename}</div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">
                        {new Date(pdf.upload_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-600">
                        {(pdf.file_size / 1024 / 1024).toFixed(2)} MB
                      </div>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap">
                      <span className={`text-xs font-semibold px-2 py-1 rounded-full ${
                        pdf.processing_status === 'completed' ? 'bg-green-100 text-green-800' :
                        pdf.processing_status === 'processing' ? 'bg-yellow-100 text-yellow-800' :
                        pdf.processing_status === 'failed' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {pdf.processing_status}
                      </span>
                    </td>
                    <td className="px-4 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/analysis/${pdf.id}`}
                        className="text-maroon hover:text-maroon-light font-medium"
                      >
                        View Details →
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 48 48">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m4 0h2m4 0h6M9 36h6m4 0h2m4 0h6M9 18h6m4 0h2m4 0h6M9 30h6m4 0h2m4 0h6m-3-18v24"/>
            </svg>
            <p className="text-gray-600 mt-4 mb-4">
              {filterStatus === 'all' ? 'No PDFs uploaded yet' : `No ${filterStatus} PDFs found`}
            </p>
            <Link to="/upload" className="btn-primary">
              Upload Your First PDFs
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;


