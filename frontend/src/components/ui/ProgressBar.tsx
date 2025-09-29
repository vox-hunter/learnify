import React from 'react';

interface ProgressBarProps {
  value: number;
  max?: number;
  min?: number;
  className?: string;
  showPercentage?: boolean;
  variant?: 'default' | 'success' | 'warning' | 'error';
  size?: 'sm' | 'md' | 'lg';
  animated?: boolean;
}

export const ProgressBar: React.FC<ProgressBarProps> = ({
  value,
  max = 100,
  min = 0,
  className = '',
  showPercentage = false,
  variant = 'default',
  size = 'md',
  animated = false
}) => {
  // Normalize value to percentage
  const normalizedValue = Math.max(min, Math.min(max, value));
  const percentage = ((normalizedValue - min) / (max - min)) * 100;

  const progressClasses = [
    'progress-bar',
    `progress-bar--${variant}`,
    `progress-bar--${size}`,
    animated ? 'progress-bar--animated' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={progressClasses} role="progressbar" aria-valuenow={normalizedValue} aria-valuemin={min} aria-valuemax={max}>
      <div className="progress-bar__track">
        <div 
          className="progress-bar__fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showPercentage && (
        <div className="progress-bar__percentage">
          {Math.round(percentage)}%
        </div>
      )}
    </div>
  );
};