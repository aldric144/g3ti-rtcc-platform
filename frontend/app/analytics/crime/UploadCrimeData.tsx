'use client';

import React, { useState, useRef } from 'react';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || 'https://g3ti-rtcc-backend.fly.dev';

interface UploadResponse {
  success: boolean;
  records_imported: number;
  errors: string[];
  message: string;
}

interface UploadCrimeDataProps {
  onUploadSuccess?: () => void;
}

export default function UploadCrimeData({ onUploadSuccess }: UploadCrimeDataProps) {
  const [isUploading, setIsUploading] = useState(false);
  const [uploadResult, setUploadResult] = useState<UploadResponse | null>(null);
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFile(e.target.files[0]);
    }
  };

  const handleFile = (file: File) => {
    const validTypes = ['.csv', '.json', '.xlsx', '.xls'];
    const fileExt = '.' + file.name.split('.').pop()?.toLowerCase();
    
    if (!validTypes.includes(fileExt)) {
      setUploadResult({
        success: false,
        records_imported: 0,
        errors: [`Invalid file type: ${fileExt}. Supported types: CSV, JSON, Excel`],
        message: 'Invalid file type',
      });
      return;
    }
    
    setSelectedFile(file);
    setUploadResult(null);
  };

  const uploadFile = async () => {
    if (!selectedFile) return;
    
    setIsUploading(true);
    setUploadResult(null);
    
    try {
      const formData = new FormData();
      formData.append('file', selectedFile);
      
      const response = await fetch(`${API_BASE_URL}/api/crime/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const result: UploadResponse = await response.json();
      setUploadResult(result);
      
      if (result.success && onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setUploadResult({
        success: false,
        records_imported: 0,
        errors: ['Network error - failed to upload file'],
        message: 'Upload failed',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const generateDemoData = async () => {
    setIsUploading(true);
    setUploadResult(null);
    
    try {
      const response = await fetch(`${API_BASE_URL}/api/crime/generate-demo-data`, {
        method: 'POST',
      });
      
      const result = await response.json();
      setUploadResult({
        success: result.success,
        records_imported: result.records_generated,
        errors: [],
        message: result.message,
      });
      
      if (result.success && onUploadSuccess) {
        onUploadSuccess();
      }
    } catch (err) {
      setUploadResult({
        success: false,
        records_imported: 0,
        errors: ['Failed to generate demo data'],
        message: 'Generation failed',
      });
    } finally {
      setIsUploading(false);
    }
  };

  const clearSelection = () => {
    setSelectedFile(null);
    setUploadResult(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-xl font-semibold text-white">Upload Crime Data</h2>
        <p className="text-gray-400 mt-1">
          Import crime data from CSV, JSON, or Excel files. Data will be normalized and added to the analysis engine.
        </p>
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
          dragActive
            ? 'border-blue-500 bg-blue-500/10'
            : 'border-gray-600 hover:border-gray-500'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv,.json,.xlsx,.xls"
          onChange={handleFileInput}
          className="hidden"
          id="file-upload"
        />
        
        {selectedFile ? (
          <div className="space-y-4">
            <div className="text-4xl">📄</div>
            <div>
              <div className="text-white font-medium">{selectedFile.name}</div>
              <div className="text-gray-500 text-sm">
                {(selectedFile.size / 1024).toFixed(1)} KB
              </div>
            </div>
            <div className="flex justify-center gap-4">
              <button
                onClick={uploadFile}
                disabled={isUploading}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {isUploading ? 'Uploading...' : 'Upload File'}
              </button>
              <button
                onClick={clearSelection}
                disabled={isUploading}
                className="px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 disabled:opacity-50"
              >
                Clear
              </button>
            </div>
          </div>
        ) : (
          <div className="space-y-4">
            <div className="text-4xl">📤</div>
            <div>
              <label
                htmlFor="file-upload"
                className="text-blue-400 hover:text-blue-300 cursor-pointer"
              >
                Click to upload
              </label>
              <span className="text-gray-400"> or drag and drop</span>
            </div>
            <div className="text-gray-500 text-sm">
              CSV, JSON, or Excel files up to 10MB
            </div>
          </div>
        )}
      </div>

      {/* Upload Result */}
      {uploadResult && (
        <div
          className={`rounded-lg p-4 ${
            uploadResult.success
              ? 'bg-green-500/20 border border-green-500'
              : 'bg-red-500/20 border border-red-500'
          }`}
        >
          <div className="flex items-start gap-3">
            <div className="text-2xl">
              {uploadResult.success ? '✓' : '✗'}
            </div>
            <div className="flex-1">
              <div className={`font-medium ${uploadResult.success ? 'text-green-400' : 'text-red-400'}`}>
                {uploadResult.message}
              </div>
              {uploadResult.records_imported > 0 && (
                <div className="text-gray-300 mt-1">
                  {uploadResult.records_imported} records imported successfully
                </div>
              )}
              {uploadResult.errors.length > 0 && (
                <div className="mt-2 space-y-1">
                  {uploadResult.errors.map((error, idx) => (
                    <div key={idx} className="text-red-400 text-sm">
                      • {error}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Data Format Guide */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Supported Data Formats</h3>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* CSV Format */}
          <div>
            <h4 className="text-white font-medium mb-2">CSV Format</h4>
            <div className="bg-gray-800 rounded p-3 text-xs font-mono text-gray-300 overflow-x-auto">
              <div>type,subcategory,date,time,latitude,longitude,sector</div>
              <div>violent,Assault,2024-01-15,14:30:00,26.7846,-80.0728,Sector 1</div>
            </div>
          </div>
          
          {/* JSON Format */}
          <div>
            <h4 className="text-white font-medium mb-2">JSON Format</h4>
            <div className="bg-gray-800 rounded p-3 text-xs font-mono text-gray-300 overflow-x-auto">
              <pre>{`[{
  "type": "violent",
  "subcategory": "Assault",
  "date": "2024-01-15",
  "latitude": 26.7846,
  "longitude": -80.0728
}]`}</pre>
            </div>
          </div>
          
          {/* Required Fields */}
          <div>
            <h4 className="text-white font-medium mb-2">Required Fields</h4>
            <ul className="text-gray-400 text-sm space-y-1">
              <li>• <span className="text-white">type</span> - Crime category</li>
              <li>• <span className="text-white">subcategory</span> - Specific crime</li>
              <li>• <span className="text-white">date</span> - YYYY-MM-DD</li>
              <li>• <span className="text-white">latitude</span> - GPS lat</li>
              <li>• <span className="text-white">longitude</span> - GPS lng</li>
            </ul>
          </div>
        </div>
        
        {/* Optional Fields */}
        <div className="mt-4 pt-4 border-t border-gray-600">
          <h4 className="text-white font-medium mb-2">Optional Fields</h4>
          <div className="flex flex-wrap gap-2">
            {['time', 'sector', 'priority', 'weapon', 'domestic_flag', 'address', 'description'].map((field) => (
              <span key={field} className="px-2 py-1 bg-gray-600 rounded text-xs text-gray-300">
                {field}
              </span>
            ))}
          </div>
        </div>
      </div>

      {/* Demo Data Generator */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-2">Generate Demo Data</h3>
        <p className="text-gray-400 text-sm mb-4">
          Don't have crime data? Generate realistic demo data for testing and demonstration purposes.
        </p>
        <button
          onClick={generateDemoData}
          disabled={isUploading}
          className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isUploading ? 'Generating...' : 'Generate 200 Demo Records'}
        </button>
      </div>

      {/* Data Sources Info */}
      <div className="bg-gray-700/50 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-white mb-4">Supported Data Sources</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <div className="bg-gray-600/50 rounded-lg p-4">
            <div className="text-blue-400 font-medium">FBI NIBRS</div>
            <div className="text-gray-400 text-sm mt-1">
              National Incident-Based Reporting System data
            </div>
          </div>
          <div className="bg-gray-600/50 rounded-lg p-4">
            <div className="text-green-400 font-medium">PBSO</div>
            <div className="text-gray-400 text-sm mt-1">
              Palm Beach County Sheriff incident reports
            </div>
          </div>
          <div className="bg-gray-600/50 rounded-lg p-4">
            <div className="text-purple-400 font-medium">Riviera Beach</div>
            <div className="text-gray-400 text-sm mt-1">
              City open data portal crime records
            </div>
          </div>
          <div className="bg-gray-600/50 rounded-lg p-4">
            <div className="text-orange-400 font-medium">Custom CSV/JSON</div>
            <div className="text-gray-400 text-sm mt-1">
              Your own formatted crime data files
            </div>
          </div>
        </div>
      </div>

      {/* Access Control Notice */}
      <div className="bg-yellow-500/10 border border-yellow-500/50 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-yellow-500 text-xl">⚠️</div>
          <div>
            <div className="text-yellow-400 font-medium">Role-Based Access</div>
            <div className="text-gray-400 text-sm mt-1">
              Only users with Analyst, Supervisor, or Admin roles can upload crime data.
              Viewer accounts have read-only access to crime analysis features.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
