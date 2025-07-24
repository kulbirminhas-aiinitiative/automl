'use client';

import { useState, useCallback } from 'react';
import { Upload, FileText, AlertCircle, CheckCircle } from 'lucide-react';

interface DataUploadProps {
  onDataUploaded: (sessionId: string) => void;
}

interface UploadResponse {
  session_id: string;
  filename: string;
  shape: [number, number];
  columns: string[];
  analysis: any;
  message: string;
}

export function DataUpload({ onDataUploaded }: DataUploadProps) {
  const [file, setFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);

  const handleFileChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFile = event.target.files?.[0];
    if (selectedFile) {
      setFile(selectedFile);
      setError(null);
      setUploadResult(null);
    }
  }, []);

  const handleUpload = async () => {
    if (!file) {
      setError('Please select a file first');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch('http://localhost:8080/api/upload-data', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Upload failed');
      }

      const result: UploadResponse = await response.json();
      setUploadResult(result);
      
      // Call the callback to switch to dashboard
      setTimeout(() => {
        onDataUploaded(result.session_id);
      }, 2000);

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred during upload');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="max-w-4xl mx-auto">
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          AutoML Solution
        </h1>
        <p className="text-xl text-gray-600 mb-8">
          Upload your dataset and let AI automatically select and train the best machine learning models
        </p>
      </div>

      <div className="bg-white rounded-xl shadow-lg p-8">
        <div className="text-center mb-6">
          <Upload className="w-16 h-16 text-blue-500 mx-auto mb-4" />
          <h2 className="text-2xl font-semibold text-gray-900 mb-2">
            Upload Your Dataset
          </h2>
          <p className="text-gray-600">
            Supported formats: CSV, XLSX, JSON
          </p>
        </div>

        <div className="space-y-6">
          {/* File Input */}
          <div className="flex items-center justify-center w-full">
            <label className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100 transition-colors">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                <FileText className="w-8 h-8 text-gray-400 mb-2" />
                <p className="mb-2 text-sm text-gray-500">
                  <span className="font-semibold">Click to upload</span> or drag and drop
                </p>
                <p className="text-xs text-gray-500">CSV, XLSX, or JSON files</p>
              </div>
              <input
                type="file"
                className="hidden"
                accept=".csv,.xlsx,.json"
                onChange={handleFileChange}
              />
            </label>
          </div>

          {/* Selected File Info */}
          {file && (
            <div className="bg-blue-50 rounded-lg p-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <FileText className="w-5 h-5 text-blue-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">{file.name}</p>
                    <p className="text-xs text-gray-500">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => setFile(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  ×
                </button>
              </div>
            </div>
          )}

          {/* Upload Button */}
          <button
            onClick={handleUpload}
            disabled={!file || loading}
            className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold disabled:opacity-50 disabled:cursor-not-allowed hover:bg-blue-700 transition-colors flex items-center justify-center space-x-2"
          >
            {loading && (
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-white border-t-transparent"></div>
            )}
            <span>{loading ? 'Analyzing Dataset...' : 'Upload and Analyze'}</span>
          </button>

          {/* Error Message */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start space-x-3">
              <AlertCircle className="w-5 h-5 text-red-500 mt-0.5" />
              <div>
                <p className="text-sm font-medium text-red-800">Upload Error</p>
                <p className="text-sm text-red-600">{error}</p>
              </div>
            </div>
          )}

          {/* Success Message */}
          {uploadResult && (
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-start space-x-3">
                <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-green-800">Upload Successful!</p>
                  <p className="text-sm text-green-600 mb-3">{uploadResult.message}</p>
                  
                  <div className="grid grid-cols-2 gap-4 text-xs">
                    <div>
                      <span className="font-medium">Dataset Shape:</span> {uploadResult.shape[0]} rows × {uploadResult.shape[1]} columns
                    </div>
                    <div>
                      <span className="font-medium">Data Quality Score:</span> {uploadResult.analysis?.data_quality?.overall_score?.toFixed(1) || 'N/A'}/100
                    </div>
                  </div>
                  
                  <p className="text-xs text-green-600 mt-2">
                    Redirecting to dashboard...
                  </p>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Features List */}
        <div className="mt-8 pt-8 border-t border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">What happens next?</h3>
          <div className="grid md:grid-cols-3 gap-4">
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-600 font-bold">1</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Data Analysis</h4>
              <p className="text-sm text-gray-600">Comprehensive analysis of your dataset structure and quality</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-600 font-bold">2</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Model Selection</h4>
              <p className="text-sm text-gray-600">AI-powered recommendations for the best ML algorithms</p>
            </div>
            <div className="text-center">
              <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-3">
                <span className="text-blue-600 font-bold">3</span>
              </div>
              <h4 className="font-medium text-gray-900 mb-1">Training & Results</h4>
              <p className="text-sm text-gray-600">Automatic training and comprehensive performance evaluation</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
