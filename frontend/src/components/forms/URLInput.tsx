import React, { useState, useCallback } from 'react';
import { documentService } from '../../services/documentService';
import type { URLDocumentResponse, APIError } from '../../types/api';
import { Input } from '../ui/Input';
import { Button } from '../ui/Button';
import { ProgressBar } from '../ui/ProgressBar';

interface URLInputProps {
  onSuccess: (response: URLDocumentResponse) => void;
  onError: (error: APIError) => void;
  placeholder?: string;
  className?: string;
}

export const URLInput: React.FC<URLInputProps> = ({
  onSuccess,
  onError,
  placeholder = 'Enter URL to process (e.g., https://example.com/document.pdf)',
  className = ''
}) => {
  const [url, setUrl] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [validationError, setValidationError] = useState('');

  const validateUrl = useCallback((urlString: string): boolean => {
    try {
      const urlObj = new URL(urlString);
      return urlObj.protocol === 'http:' || urlObj.protocol === 'https:';
    } catch {
      return false;
    }
  }, []);

  const handleUrlChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const newUrl = e.target.value;
    setUrl(newUrl);
    
    // Clear validation error when user types
    if (validationError) {
      setValidationError('');
    }
  }, [validationError]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!url.trim()) {
      setValidationError('Please enter a URL');
      return;
    }

    if (!validateUrl(url.trim())) {
      setValidationError('Please enter a valid HTTP or HTTPS URL');
      return;
    }

    setIsProcessing(true);
    setProgress(0);
    setValidationError('');

    try {
      const response = await documentService.processUrlDocument(
        url.trim(),
        {}
      );
      onSuccess(response);
      setUrl(''); // Clear input on success
    } catch (error) {
      onError(error as APIError);
    } finally {
      setIsProcessing(false);
      setProgress(0);
    }
  }, [url, validateUrl, onSuccess, onError]);

  const handleKeyPress = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !isProcessing) {
      handleSubmit(e as React.FormEvent);
    }
  }, [handleSubmit, isProcessing]);

  return (
    <div className={`url-input ${className}`}>
      <form onSubmit={handleSubmit} className="url-form">
        <div className="url-input-group">
          <Input
            type="url"
            value={url}
            onChange={handleUrlChange}
            onKeyPress={handleKeyPress}
            placeholder={placeholder}
            disabled={isProcessing}
            error={validationError}
            className="url-field"
          />
          <Button
            type="submit"
            disabled={isProcessing || !url.trim()}
            className="process-button"
          >
            {isProcessing ? 'Processing...' : 'Process URL'}
          </Button>
        </div>
        
        {validationError && (
          <div className="error-message">
            {validationError}
          </div>
        )}
        
        {isProcessing && (
          <div className="processing-status">
            <ProgressBar
              value={progress}
              max={100}
              className="process-progress"
            />
            <p className="process-text">
              Processing URL... {Math.round(progress)}%
            </p>
          </div>
        )}
      </form>
    </div>
  );
};