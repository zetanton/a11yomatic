import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { pdfAPI, reportsAPI } from '../../services/api';

const Dashboard: React.FC = () => {
  const { data: pdfs, isLoading: pdfsLoading } = useQuery({
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
        return 'text-green-400';
      case 'processing':
        return 'text-yellow-400';
      case 'failed':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-gray-400 mt-2">
          Manage your PDF accessibility analysis and remediation
        </p>
      </div>

      {/* Analytics Cards */}
      {analytics && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card">
            <div className="text-sm text-gray-400">Total PDFs</div>
            <div className="text-3xl font-bold text-primary-500 mt-2">
              {analytics.total_pdfs}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Total Issues</div>
            <div className="text-3xl font-bold text-orange-500 mt-2">
              {analytics.total_issues}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Average Score</div>
            <div className="text-3xl font-bold text-green-500 mt-2">
              {analytics.average_score}
            </div>
          </div>
          <div className="card">
            <div className="text-sm text-gray-400">Critical Issues</div>
            <div className="text-3xl font-bold text-red-500 mt-2">
              {analytics.issue_breakdown.critical}
            </div>
          </div>
        </div>
      )}

      {/* Recent PDFs */}
      <div className="card">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-semibold">Recent PDFs</h2>
          <Link to="/upload" className="btn-primary">
            Upload New PDF
          </Link>
        </div>

        {pdfsLoading ? (
          <div className="text-center py-12">
            <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500"></div>
            <p className="text-gray-400 mt-4">Loading PDFs...</p>
          </div>
        ) : pdfs && pdfs.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-dark-700">
              <thead>
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Filename
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Upload Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Size
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-dark-700">
                {pdfs.map((pdf: any) => (
                  <tr key={pdf.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-200">{pdf.filename}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-400">
                        {new Date(pdf.upload_date).toLocaleDateString()}
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-400">
                        {(pdf.file_size / 1024).toFixed(2)} KB
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getStatusColor(pdf.processing_status)}`}>
                        {pdf.processing_status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <Link
                        to={`/analysis/${pdf.id}`}
                        className="text-primary-500 hover:text-primary-400 mr-4"
                      >
                        View Analysis
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-12">
            <p className="text-gray-400 mb-4">No PDFs uploaded yet</p>
            <Link to="/upload" className="btn-primary">
              Upload Your First PDF
            </Link>
          </div>
        )}
      </div>
    </div>
  );
};

export default Dashboard;


