import React, { useCallback, useState } from 'react';
import { documentService } from '../../services/documentService';
import type { DocumentUploadResponse, APIError } from '../../types/api';
import { ProgressBar } from '../ui/ProgressBar';
import { Button } from '../ui/Button';

interface FileUploadProps {
  onSuccess: (response: DocumentUploadResponse) => void;
  onError: (error: APIError) => void;
  acceptedTypes?: string[];
  maxSize?: number;
  className?: string;
}

export const FileUpload: React.FC<FileUploadProps> = ({
  onSuccess,
  onError,
  acceptedTypes = ['.pdf', '.doc', '.docx', '.txt'],
  maxSize = 10 * 1024 * 1024, // 10MB
  className = ''
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    
    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      setSelectedFile(files[0]);
    }
  }, []);

  const handleFileSelect = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      setSelectedFile(files[0]);
    }
  }, []);

  const handleUpload = useCallback(async () => {
    if (!selectedFile) return;

    setIsUploading(true);
    setUploadProgress(0);

    try {
      const response = await documentService.uploadDocument(
        selectedFile,
        { title: selectedFile.name }
      );
      onSuccess(response);
      setSelectedFile(null);
    } catch (error) {
      onError(error as APIError);
    } finally {
      setIsUploading(false);
      setUploadProgress(0);
    }
  }, [selectedFile, onSuccess, onError]);

  const handleRemoveFile = useCallback(() => {
    setSelectedFile(null);
  }, []);

  return (
    <div className={`file-upload ${className}`}>
      {!selectedFile ? (
        <div
          className={`upload-area ${
            isDragging ? 'dragging' : ''
          } ${isUploading ? 'uploading' : ''}`}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div className="upload-content">
            <div className="upload-icon">📁</div>
            <p className="upload-text">
              Drag and drop a file here, or{' '}
              <label className="file-input-label">
                <input
                  type="file"
                  accept={acceptedTypes.join(',')}
                  onChange={handleFileSelect}
                  className="file-input"
                  disabled={isUploading}
                />
                click to browse
              </label>
            </p>
            <p className="upload-hint">
              Supported formats: {acceptedTypes.join(', ')}
              <br />
              Maximum size: {Math.round(maxSize / (1024 * 1024))}MB
            </p>
          </div>
        </div>
      ) : (
        <div className="file-selected">
          <div className="file-info">
            <div className="file-icon">📄</div>
            <div className="file-details">
              <p className="file-name">{selectedFile.name}</p>
              <p className="file-size">
                {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
              </p>
            </div>
            <Button
              variant="ghost"
              size="sm"
              onClick={handleRemoveFile}
              disabled={isUploading}
              className="remove-file"
            >
              ✕
            </Button>
          </div>
          
          {isUploading && (
            <ProgressBar
              value={uploadProgress}
              max={100}
              className="upload-progress"
            />
          )}
          
          <div className="file-actions">
            <Button
              onClick={handleUpload}
              disabled={isUploading}
              className="upload-button"
            >
              {isUploading ? 'Uploading...' : 'Upload File'}
            </Button>
          </div>
        </div>
      )}
    </div>
  );
};