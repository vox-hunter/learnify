import React, { forwardRef } from 'react';
import styles from '../../styles/Button.module.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'ghost' | 'danger' | 'gradient';
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
    styles.button,
    styles[`button--${variant}`],
    styles[`button--${size}`],
    fullWidth ? styles['button--full-width'] : '',
    isLoading ? styles['button--loading'] : '',
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
        <span className={styles.button__spinner} aria-hidden="true">
          ⏳
        </span>
      )}
      
      {!isLoading && leftIcon && (
        <span className={styles.button__left_icon} aria-hidden="true">
          {leftIcon}
        </span>
      )}
      
      <span className={styles.button__text}>
        {children}
      </span>
      
      {!isLoading && rightIcon && (
        <span className={styles.button__right_icon} aria-hidden="true">
          {rightIcon}
        </span>
      )}
    </button>
  );
});

Button.displayName = 'Button';