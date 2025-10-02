import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { useNavigate } from 'react-router-dom';
import { useDispatch } from 'react-redux';
import { addDocument, setUploadProgress, setIsUploading } from '../../store/slices/pdfSlice';
import apiService from '../../services/api';

const PDFUpload: React.FC = () => {
  const [uploadedFiles, setUploadedFiles] = useState<any[]>([]);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const dispatch = useDispatch();

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    setError('');
    dispatch(setIsUploading(true));
    dispatch(setUploadProgress(0));

    for (const file of acceptedFiles) {
      try {
        const response: any = await apiService.uploadPDF(file);
        dispatch(addDocument(response));
        setUploadedFiles((prev) => [...prev, response]);
        dispatch(setUploadProgress(100));
        
        // Auto-start analysis
        await apiService.startAnalysis(response.id);
      } catch (err: any) {
        setError(err.message || 'Upload failed');
      }
    }

    dispatch(setIsUploading(false));
  }, [dispatch]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxSize: 100 * 1024 * 1024, // 100MB
    multiple: true,
  });

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white">Upload PDFs</h1>
        {uploadedFiles.length > 0 && (
          <button
            onClick={() => navigate('/pdfs')}
            className="btn btn-primary"
          >
            View All PDFs
          </button>
        )}
      </div>

      {error && (
        <div className="bg-red-900/20 border border-red-500 rounded-lg p-4">
          <p className="text-red-400">{error}</p>
        </div>
      )}

      <div className="card">
        <div
          {...getRootProps()}
          className={`upload-area ${
            isDragActive ? 'border-primary-500 bg-primary-500/10' : ''
          }`}
        >
          <input {...getInputProps()} />
          <div className="text-center">
            <svg
              className="mx-auto h-12 w-12 text-primary-500"
              stroke="currentColor"
              fill="none"
              viewBox="0 0 48 48"
              aria-hidden="true"
            >
              <path
                d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8m-12 4h.02"
                strokeWidth={2}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
            <div className="mt-4">
              <p className="text-lg text-gray-200">
                {isDragActive
                  ? 'Drop the files here...'
                  : 'Drag and drop PDF files here, or click to browse'}
              </p>
              <p className="mt-2 text-sm text-gray-400">
                Maximum file size: 100MB per file
              </p>
            </div>
          </div>
        </div>
      </div>

      {uploadedFiles.length > 0 && (
        <div className="card">
          <h2 className="text-xl font-bold text-white mb-4">
            Recently Uploaded
          </h2>
          <div className="space-y-3">
            {uploadedFiles.map((file) => (
              <div
                key={file.id}
                className="flex items-center justify-between p-4 bg-dark-800 rounded-lg"
              >
                <div className="flex items-center space-x-3">
                  <svg
                    className="h-8 w-8 text-primary-500"
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
                    <p className="font-medium text-white">{file.filename}</p>
                    <p className="text-sm text-gray-400">
                      {(file.file_size / 1024 / 1024).toFixed(2)} MB • {file.page_count || 0} pages
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => navigate(`/analysis/${file.id}`)}
                  className="btn btn-secondary"
                >
                  View Analysis
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default PDFUpload;
