import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import apiService from '../../services/api';

const PDFList: React.FC = () => {
  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['pdfs'],
    queryFn: () => apiService.listPDFs(),
  });

  const handleDelete = async (pdfId: string) => {
    if (window.confirm('Are you sure you want to delete this PDF?')) {
      try {
        await apiService.deletePDF(pdfId);
        refetch();
      } catch (err) {
        console.error('Failed to delete PDF:', err);
      }
    }
  };

  if (isLoading) {
    return (
      <div className="text-center py-12">
        <div className="text-gray-400">Loading PDFs...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
        <p className="text-red-400">Failed to load PDFs</p>
      </div>
    );
  }

  const pdfs = data?.pdfs || [];

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">My PDFs</h1>
        <Link to="/upload" className="btn btn-primary">
          Upload New PDF
        </Link>
      </div>

      {pdfs.length === 0 ? (
        <div className="card text-center py-12">
          <svg
            className="mx-auto h-12 w-12 text-gray-500"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
            />
          </svg>
          <h3 className="mt-4 text-lg font-medium text-white">No PDFs yet</h3>
          <p className="mt-2 text-gray-400">
            Get started by uploading your first PDF document.
          </p>
          <Link to="/upload" className="mt-4 inline-block btn btn-primary">
            Upload PDF
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6">
          {pdfs.map((pdf: any) => (
            <div key={pdf.id} className="card">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <svg
                    className="h-12 w-12 text-primary-500"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"
                    />
                  </svg>
                  <div>
                    <h3 className="text-lg font-medium text-white">
                      {pdf.filename}
                    </h3>
                    <div className="mt-1 flex items-center space-x-4 text-sm text-gray-400">
                      <span>{(pdf.file_size / 1024 / 1024).toFixed(2)} MB</span>
                      <span>•</span>
                      <span>{pdf.page_count || 0} pages</span>
                      <span>•</span>
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          pdf.processing_status === 'completed'
                            ? 'bg-green-900/20 text-green-400'
                            : pdf.processing_status === 'analyzing'
                            ? 'bg-yellow-900/20 text-yellow-400'
                            : pdf.processing_status === 'failed'
                            ? 'bg-red-900/20 text-red-400'
                            : 'bg-gray-900/20 text-gray-400'
                        }`}
                      >
                        {pdf.processing_status}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-2">
                  {pdf.processing_status === 'completed' && (
                    <Link
                      to={`/analysis/${pdf.id}`}
                      className="btn btn-primary"
                    >
                      View Analysis
                    </Link>
                  )}
                  {pdf.processing_status === 'uploaded' && (
                    <button
                      onClick={async () => {
                        await apiService.startAnalysis(pdf.id);
                        refetch();
                      }}
                      className="btn btn-secondary"
                    >
                      Start Analysis
                    </button>
                  )}
                  <button
                    onClick={() => handleDelete(pdf.id)}
                    className="btn btn-danger"
                  >
                    Delete
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default PDFList;
