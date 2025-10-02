import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import apiService from '../../services/api';

const Dashboard: React.FC = () => {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: () => apiService.getAnalytics(),
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Dashboard</h1>
        <Link to="/upload" className="btn btn-primary">
          Upload PDF
        </Link>
      </div>

      {isLoading ? (
        <div className="text-center py-12">
          <div className="text-gray-400">Loading analytics...</div>
        </div>
      ) : (
        <>
          {/* Analytics Cards */}
          <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400">Total PDFs</h3>
              <p className="mt-2 text-3xl font-bold text-white">
                {analytics?.total_pdfs || 0}
              </p>
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400">Total Issues</h3>
              <p className="mt-2 text-3xl font-bold text-white">
                {analytics?.total_issues || 0}
              </p>
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400">Average Score</h3>
              <p className="mt-2 text-3xl font-bold text-white">
                {analytics?.average_score || 0}
              </p>
            </div>
            <div className="card">
              <h3 className="text-sm font-medium text-gray-400">Critical Issues</h3>
              <p className="mt-2 text-3xl font-bold text-red-500">
                {analytics?.severity_distribution?.critical || 0}
              </p>
            </div>
          </div>

          {/* Quick Actions */}
          <div className="card">
            <h2 className="text-xl font-bold text-white mb-4">Quick Actions</h2>
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <Link
                to="/upload"
                className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center"
              >
                <div className="text-primary-500 text-2xl mb-2">📤</div>
                <div className="text-white font-medium">Upload PDF</div>
                <div className="text-gray-400 text-sm">
                  Start analyzing a new document
                </div>
              </Link>
              <Link
                to="/pdfs"
                className="p-4 bg-dark-800 rounded-lg hover:bg-dark-700 transition-colors text-center"
              >
                <div className="text-primary-500 text-2xl mb-2">📄</div>
                <div className="text-white font-medium">View PDFs</div>
                <div className="text-gray-400 text-sm">
                  Browse your uploaded documents
                </div>
              </Link>
              <div className="p-4 bg-dark-800 rounded-lg text-center opacity-50">
                <div className="text-primary-500 text-2xl mb-2">📊</div>
                <div className="text-white font-medium">Reports</div>
                <div className="text-gray-400 text-sm">
                  View detailed accessibility reports
                </div>
              </div>
            </div>
          </div>

          {/* Severity Distribution */}
          {analytics?.severity_distribution && (
            <div className="card">
              <h2 className="text-xl font-bold text-white mb-4">
                Issue Distribution
              </h2>
              <div className="space-y-3">
                {Object.entries(analytics.severity_distribution).map(
                  ([severity, count]) => (
                    <div key={severity} className="flex items-center">
                      <div className="flex-1">
                        <div className="flex justify-between mb-1">
                          <span className="text-sm font-medium text-gray-300 capitalize">
                            {severity}
                          </span>
                          <span className="text-sm text-gray-400">{count}</span>
                        </div>
                        <div className="w-full bg-dark-700 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              severity === 'critical'
                                ? 'bg-red-500'
                                : severity === 'high'
                                ? 'bg-orange-500'
                                : severity === 'medium'
                                ? 'bg-yellow-500'
                                : 'bg-blue-500'
                            }`}
                            style={{
                              width: `${
                                (count / (analytics.total_issues || 1)) * 100
                              }%`,
                            }}
                          />
                        </div>
                      </div>
                    </div>
                  )
                )}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default Dashboard;
