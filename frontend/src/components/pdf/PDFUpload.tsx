import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { pdfAPI, analysisAPI } from '../../services/api';
import { addDocument } from '../../store/slices/pdfSlice';

interface UploadItem {
  file: File;
  id: string;
  status: 'pending' | 'uploading' | 'analyzing' | 'completed' | 'error';
  progress: number;
  error?: string;
  pdfId?: string;
}

const PDFUpload: React.FC = () => {
  const [uploadQueue, setUploadQueue] = useState<UploadItem[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState('');
  
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const processUploadQueue = async (files: File[]) => {
    setIsProcessing(true);
    setError('');

    // Initialize queue
    const queue: UploadItem[] = files.map((file, index) => ({
      file,
      id: `${Date.now()}-${index}`,
      status: 'pending',
      progress: 0,
    }));
    setUploadQueue(queue);

    // Process files sequentially
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i];
      
      try {
        // Update status to uploading
        setUploadQueue(prev => prev.map(q => 
          q.id === item.id ? { ...q, status: 'uploading' as const } : q
        ));

        // Upload PDF
        const response = await pdfAPI.upload(item.file, (progress) => {
          setUploadQueue(prev => prev.map(q => 
            q.id === item.id ? { ...q, progress } : q
          ));
        });

        const pdfData = response.data;
        dispatch(addDocument(pdfData));

        // Update status to analyzing
        setUploadQueue(prev => prev.map(q => 
          q.id === item.id ? { ...q, status: 'analyzing' as const, pdfId: pdfData.id } : q
        ));

        // Start analysis
        await analysisAPI.analyze(pdfData.id);

        // Mark as completed
        setUploadQueue(prev => prev.map(q => 
          q.id === item.id ? { ...q, status: 'completed' as const, progress: 100 } : q
        ));

      } catch (err: any) {
        setUploadQueue(prev => prev.map(q => 
          q.id === item.id ? { 
            ...q, 
            status: 'error' as const, 
            error: err.response?.data?.detail || 'Upload failed' 
          } : q
        ));
      }
    }

    setIsProcessing(false);
    
    // Auto-navigate if single file
    if (files.length === 1 && queue[0].pdfId) {
      setTimeout(() => {
        navigate('/');
      }, 1500);
    } else if (files.length > 1) {
      setTimeout(() => {
        navigate('/');
      }, 2000);
    }
  };

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;
    await processUploadQueue(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 100 * 1024 * 1024, // 100MB per file
    multiple: true,
    disabled: isProcessing,
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Upload PDFs for Analysis</h1>
        <p className="text-gray-600">
          Drag and drop PDF files or folders, or click to browse
        </p>
        <p className="text-sm text-gray-500 mt-2">
          Support for multiple files and bulk uploads
        </p>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-300 text-red-800 px-4 py-3 rounded-lg mb-6">
          {error}
        </div>
      )}

      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-lg p-12 text-center cursor-pointer
          transition-colors duration-200
          ${
            isDragActive
              ? 'border-maroon bg-maroon/10'
              : 'border-gray-300 hover:border-maroon hover:bg-gray-50'
          }
          ${isProcessing ? 'opacity-50 pointer-events-none' : ''}
        `}
      >
        <input {...getInputProps()} />

        <div className="space-y-4">
          <svg
            className="mx-auto h-16 w-16 text-gray-400"
            stroke="currentColor"
            fill="none"
            viewBox="0 0 48 48"
          >
            <path
              d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
          </svg>

          <div>
            <p className="text-lg text-gray-700 mb-2">
              {isDragActive
                ? 'Drop the PDF files here'
                : 'Drag & drop PDF files or folders here, or click to select'}
            </p>
            <p className="text-sm text-gray-600">
              Maximum file size: 100MB per file • Multiple files supported
            </p>
          </div>
        </div>
      </div>

      {/* Upload Queue */}
      {uploadQueue.length > 0 && (
        <div className="mt-6 space-y-3">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-lg font-semibold">
              Upload Queue ({uploadQueue.filter(q => q.status === 'completed').length}/{uploadQueue.length})
            </h3>
            {!isProcessing && uploadQueue.some(q => q.status === 'completed') && (
              <button
                onClick={() => navigate('/')}
                className="btn-primary text-sm"
              >
                Go to Dashboard
              </button>
            )}
          </div>

          {uploadQueue.map((item) => (
            <div key={item.id} className="card">
              <div className="flex items-center justify-between mb-2">
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-gray-900 truncate">
                    {item.file.name}
                  </p>
                  <p className="text-xs text-gray-500">
                    {(item.file.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
                <div className="ml-4">
                  {item.status === 'pending' && (
                    <span className="badge bg-gray-100 text-gray-800">Pending</span>
                  )}
                  {item.status === 'uploading' && (
                    <span className="badge bg-blue-100 text-blue-800">Uploading {item.progress}%</span>
                  )}
                  {item.status === 'analyzing' && (
                    <span className="badge bg-yellow-100 text-yellow-800">Analyzing...</span>
                  )}
                  {item.status === 'completed' && (
                    <span className="badge bg-green-100 text-green-800">✓ Completed</span>
                  )}
                  {item.status === 'error' && (
                    <span className="badge bg-red-100 text-red-800">✗ Error</span>
                  )}
                </div>
              </div>

              {(item.status === 'uploading' || item.status === 'analyzing') && (
                <div className="w-full bg-gray-200 rounded-full h-2 mt-2">
                  <div
                    className="bg-maroon h-2 rounded-full transition-all duration-300"
                    style={{ width: `${item.progress}%` }}
                  />
                </div>
              )}

              {item.error && (
                <p className="text-xs text-red-600 mt-2">{item.error}</p>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Info Cards */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Automated Analysis</h3>
          <p className="text-sm text-gray-600">
            Our AI automatically scans your PDF for accessibility issues
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">AI-Powered Solutions</h3>
          <p className="text-sm text-gray-600">
            Get intelligent remediation suggestions powered by advanced AI
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">WCAG Compliance</h3>
          <p className="text-sm text-gray-600">
            Ensure your PDFs meet WCAG 2.1 and Section 508 standards
          </p>
        </div>
      </div>
    </div>
  );
};

export default PDFUpload;


