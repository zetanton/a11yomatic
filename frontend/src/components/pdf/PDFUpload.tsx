import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { pdfAPI, analysisAPI } from '../../services/api';
import { addDocument, setUploadProgress, setIsUploading } from '../../store/slices/pdfSlice';

const PDFUpload: React.FC = () => {
  const [uploadProgress, setProgress] = useState(0);
  const [isUploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [uploadedPdfId, setUploadedPdfId] = useState<string | null>(null);
  
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    if (acceptedFiles.length === 0) return;

    const file = acceptedFiles[0];
    setError('');
    setUploading(true);
    setProgress(0);

    try {
      // Upload PDF
      const response = await pdfAPI.upload(file, (progress) => {
        setProgress(progress);
      });

      const pdfData = response.data;
      dispatch(addDocument(pdfData));
      setUploadedPdfId(pdfData.id);

      // Start analysis
      await analysisAPI.analyze(pdfData.id);

      // Redirect to analysis page after a short delay
      setTimeout(() => {
        navigate(`/analysis/${pdfData.id}`);
      }, 1000);

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Upload failed. Please try again.');
      setUploading(false);
    }
  }, [dispatch, navigate]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf']
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: false,
    disabled: isUploading,
  });

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-4">Upload PDF for Analysis</h1>
        <p className="text-gray-400">
          Drag and drop your PDF file or click to browse
        </p>
      </div>

      {error && (
        <div className="bg-red-900/50 border border-red-700 text-red-200 px-4 py-3 rounded-lg mb-6">
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
              ? 'border-primary-500 bg-primary-900/20'
              : 'border-dark-600 hover:border-primary-500 hover:bg-dark-800'
          }
          ${isUploading ? 'opacity-50 pointer-events-none' : ''}
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
            <p className="text-lg text-gray-300 mb-2">
              {isDragActive
                ? 'Drop the PDF file here'
                : 'Drag & drop a PDF file here, or click to select'}
            </p>
            <p className="text-sm text-gray-500">
              Maximum file size: 100MB
            </p>
          </div>
        </div>
      </div>

      {isUploading && (
        <div className="mt-6 card">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm text-gray-300">
                {uploadProgress < 100 ? 'Uploading...' : 'Processing...'}
              </span>
              <span className="text-sm text-gray-400">{uploadProgress}%</span>
            </div>
            <div className="w-full bg-dark-700 rounded-full h-2">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${uploadProgress}%` }}
              />
            </div>
            {uploadProgress === 100 && (
              <p className="text-sm text-gray-400 text-center">
                Starting accessibility analysis...
              </p>
            )}
          </div>
        </div>
      )}

      {/* Info Cards */}
      <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">Automated Analysis</h3>
          <p className="text-sm text-gray-400">
            Our AI automatically scans your PDF for accessibility issues
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">AI-Powered Solutions</h3>
          <p className="text-sm text-gray-400">
            Get intelligent remediation suggestions powered by advanced AI
          </p>
        </div>
        <div className="card">
          <h3 className="text-lg font-semibold mb-2">WCAG Compliance</h3>
          <p className="text-sm text-gray-400">
            Ensure your PDFs meet WCAG 2.1 and Section 508 standards
          </p>
        </div>
      </div>
    </div>
  );
};

export default PDFUpload;
