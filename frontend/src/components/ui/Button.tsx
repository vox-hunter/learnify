import React, { forwardRef } from 'react';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
  size?: 'sm' | 'md' | 'lg';
  isLoading?: boolean;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
  fullWidth?: boolean;
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>((
  {
    children,
    variant = 'primary',
    size = 'md',
    isLoading = false,
    leftIcon,
    rightIcon,
    fullWidth = false,
    className = '',
    disabled,
    ...props
  },
  ref
) => {
  const buttonClasses = [
    'button',
    `button--${variant}`,
    `button--${size}`,
    fullWidth ? 'button--full-width' : '',
    isLoading ? 'button--loading' : '',
    className
  ].filter(Boolean).join(' ');

  const isDisabled = disabled || isLoading;

  return (
    <button
      ref={ref}
      className={buttonClasses}
      disabled={isDisabled}
      {...props}
    >
      {isLoading && (
        <span className="button__spinner" aria-hidden="true">
          ⏳
        </span>
      )}
      
      {!isLoading && leftIcon && (
        <span className="button__left-icon" aria-hidden="true">
          {leftIcon}
        </span>
      )}
      
      <span className="button__text">
        {children}
      </span>
      
      {!isLoading && rightIcon && (
        <span className="button__right-icon" aria-hidden="true">
          {rightIcon}
        </span>
      )}
    </button>
  );
});

Button.displayName = 'Button';