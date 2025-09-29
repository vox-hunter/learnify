/**
 * Form Validation Utilities
 * Provides comprehensive validation rules and helpers
 */

export interface ValidationRule<T = unknown> {
  test: (value: T) => boolean;
  message: string;
}

export interface ValidationResult {
  isValid: boolean;
  errors: string[];
}

export type Validator<T = unknown> = (value: T) => ValidationResult;

/**
 * Common validation rules
 */
export const validationRules = {
  required: (message = 'This field is required'): ValidationRule<unknown> => ({
    test: (value) => {
      if (typeof value === 'string') return value.trim().length > 0;
      if (Array.isArray(value)) return value.length > 0;
      return value != null;
    },
    message,
  }),

  minLength: (min: number, message?: string): ValidationRule<string> => ({
    test: (value) => !value || value.length >= min,
    message: message || `Must be at least ${min} characters`,
  }),

  maxLength: (max: number, message?: string): ValidationRule<string> => ({
    test: (value) => !value || value.length <= max,
    message: message || `Must not exceed ${max} characters`,
  }),

  pattern: (regex: RegExp, message: string): ValidationRule<string> => ({
    test: (value) => !value || regex.test(value),
    message,
  }),

  email: (message = 'Invalid email address'): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      return emailRegex.test(value);
    },
    message,
  }),

  phone: (message = 'Invalid phone number'): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const phoneRegex = /^[+]?[1-9][\d]{0,15}$/;
      return phoneRegex.test(value.replace(/[\s-()]/g, ''));
    },
    message,
  }),

  url: (message = 'Invalid URL'): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      try {
        new URL(value);
        return true;
      } catch {
        return false;
      }
    },
    message,
  }),

  number: (message = 'Must be a valid number'): ValidationRule<string> => ({
    test: (value) => !value || !isNaN(Number(value)),
    message,
  }),

  integer: (message = 'Must be a whole number'): ValidationRule<string> => ({
    test: (value) => !value || Number.isInteger(Number(value)),
    message,
  }),

  positive: (message = 'Must be a positive number'): ValidationRule<string> => ({
    test: (value) => !value || Number(value) > 0,
    message,
  }),

  min: (min: number, message?: string): ValidationRule<string> => ({
    test: (value) => !value || Number(value) >= min,
    message: message || `Must be at least ${min}`,
  }),

  max: (max: number, message?: string): ValidationRule<string> => ({
    test: (value) => !value || Number(value) <= max,
    message: message || `Must not exceed ${max}`,
  }),

  date: (message = 'Invalid date'): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return !isNaN(date.getTime());
    },
    message,
  }),

  minDate: (minDate: Date, message?: string): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return date >= minDate;
    },
    message: message || `Date must be after ${minDate.toLocaleDateString()}`,
  }),

  maxDate: (maxDate: Date, message?: string): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const date = new Date(value);
      return date <= maxDate;
    },
    message: message || `Date must be before ${maxDate.toLocaleDateString()}`,
  }),

  password: (message = 'Password must be at least 8 characters with uppercase, lowercase, number, and special character'): ValidationRule<string> => ({
    test: (value) => {
      if (!value) return true;
      const hasUpper = /[A-Z]/.test(value);
      const hasLower = /[a-z]/.test(value);
      const hasNumber = /\d/.test(value);
      const hasSpecial = /[!@#$%^&*(),.?":{}|<>]/.test(value);
      const hasMinLength = value.length >= 8;
      return hasUpper && hasLower && hasNumber && hasSpecial && hasMinLength;
    },
    message,
  }),

  confirmPassword: (originalPassword: string, message = 'Passwords do not match'): ValidationRule<string> => ({
    test: (value) => value === originalPassword,
    message,
  }),

  fileSize: (maxSizeInMB: number, message?: string): ValidationRule<File> => ({
    test: (file) => {
      if (!file) return true;
      const maxSizeInBytes = maxSizeInMB * 1024 * 1024;
      return file.size <= maxSizeInBytes;
    },
    message: message || `File size must not exceed ${maxSizeInMB}MB`,
  }),

  fileType: (allowedTypes: string[], message?: string): ValidationRule<File> => ({
    test: (file) => {
      if (!file) return true;
      return allowedTypes.includes(file.type);
    },
    message: message || `File type must be one of: ${allowedTypes.join(', ')}`,
  }),

  custom: <T>(test: (value: T) => boolean, message: string): ValidationRule<T> => ({
    test,
    message,
  }),
} as const;

/**
 * Create a validator from multiple rules
 */
export const createValidator = <T>(...rules: ValidationRule<T>[]): Validator<T> => {
  return (value: T): ValidationResult => {
    const errors: string[] = [];
    
    for (const rule of rules) {
      if (!rule.test(value)) {
        errors.push(rule.message);
      }
    }
    
    return {
      isValid: errors.length === 0,
      errors,
    };
  };
};

/**
 * Validate an object with field validators
 */
export type FieldValidators<T> = {
  [K in keyof T]?: Validator<T[K]>;
};

export interface FormValidationResult<T> {
  isValid: boolean;
  errors: Partial<Record<keyof T, string[]>>;
}

export const validateForm = <T extends Record<string, unknown>>(
  data: T,
  validators: FieldValidators<T>
): FormValidationResult<T> => {
  const errors: Partial<Record<keyof T, string[]>> = {};
  let isValid = true;

  for (const [field, validator] of Object.entries(validators) as [keyof T, Validator<T[keyof T]>][]) {
    if (validator && data[field] !== undefined) {
      const result = validator(data[field]);
      if (!result.isValid) {
        errors[field] = result.errors;
        isValid = false;
      }
    }
  }

  return { isValid, errors };
};

/**
 * Async validation support
 */
export type AsyncValidator<T = unknown> = (value: T) => Promise<ValidationResult>;

export const createAsyncValidator = <T>(
  asyncTest: (value: T) => Promise<boolean>,
  message: string
): AsyncValidator<T> => {
  return async (value: T): Promise<ValidationResult> => {
    try {
      const isValid = await asyncTest(value);
      return {
        isValid,
        errors: isValid ? [] : [message],
      };
    } catch {
      return {
        isValid: false,
        errors: [message],
      };
    }
  };
};

/**
 * Common async validators
 */
export const asyncValidationRules = {
  uniqueEmail: (checkEmail: (email: string) => Promise<boolean>, message = 'Email is already taken'): AsyncValidator<string> =>
    createAsyncValidator(async (email: string) => {
      if (!email) return true;
      return await checkEmail(email);
    }, message),

  uniqueUsername: (checkUsername: (username: string) => Promise<boolean>, message = 'Username is already taken'): AsyncValidator<string> =>
    createAsyncValidator(async (username: string) => {
      if (!username) return true;
      return await checkUsername(username);
    }, message),
};

/**
 * Form field validation hook
 */
export const useFieldValidation = <T>(
  initialValue: T,
  validator?: Validator<T>,
  asyncValidator?: AsyncValidator<T>
) => {
  const [value, setValue] = React.useState<T>(initialValue);
  const [errors, setErrors] = React.useState<string[]>([]);
  const [isValidating, setIsValidating] = React.useState(false);
  const [touched, setTouched] = React.useState(false);

  const validate = React.useCallback(async (valueToValidate: T = value) => {
    let validationErrors: string[] = [];

    // Sync validation
    if (validator) {
      const result = validator(valueToValidate);
      validationErrors = result.errors;
    }

    // Async validation (only if sync validation passes)
    if (validationErrors.length === 0 && asyncValidator) {
      setIsValidating(true);
      try {
        const result = await asyncValidator(valueToValidate);
        validationErrors = result.errors;
      } catch {
        validationErrors = ['Validation failed'];
      } finally {
        setIsValidating(false);
      }
    }

    setErrors(validationErrors);
    return validationErrors.length === 0;
  }, [value, validator, asyncValidator]);

  const handleChange = React.useCallback((newValue: T) => {
    setValue(newValue);
    if (touched) {
      validate(newValue);
    }
  }, [touched, validate]);

  const handleBlur = React.useCallback(() => {
    setTouched(true);
    validate();
  }, [validate]);

  const reset = React.useCallback(() => {
    setValue(initialValue);
    setErrors([]);
    setTouched(false);
    setIsValidating(false);
  }, [initialValue]);

  return {
    value,
    setValue: handleChange,
    errors,
    isValidating,
    touched,
    isValid: errors.length === 0 && !isValidating,
    validate,
    onBlur: handleBlur,
    reset,
  };
};

/**
 * Form validation hook
 */
export const useFormValidation = <T extends Record<string, unknown>>(
  initialData: T,
  validators: FieldValidators<T>,
  asyncValidators?: Partial<Record<keyof T, AsyncValidator<T[keyof T]>>>
) => {
  const [data, setData] = React.useState<T>(initialData);
  const [errors, setErrors] = React.useState<Partial<Record<keyof T, string[]>>>({});
  const [touched, setTouched] = React.useState<Partial<Record<keyof T, boolean>>>({});
  const [isValidating, setIsValidating] = React.useState(false);

  const validateField = React.useCallback(async (field: keyof T, value: T[keyof T]) => {
    const validator = validators[field];
    const asyncValidator = asyncValidators?.[field];
    let fieldErrors: string[] = [];

    // Sync validation
    if (validator) {
      const result = validator(value);
      fieldErrors = result.errors;
    }

    // Async validation (only if sync validation passes)
    if (fieldErrors.length === 0 && asyncValidator) {
      setIsValidating(true);
      try {
        const result = await asyncValidator(value);
        fieldErrors = result.errors;
      } catch {
        fieldErrors = ['Validation failed'];
      } finally {
        setIsValidating(false);
      }
    }

    setErrors(prev => ({
      ...prev,
      [field]: fieldErrors.length > 0 ? fieldErrors : undefined,
    }));

    return fieldErrors.length === 0;
  }, [validators, asyncValidators]);

  const validateForm = React.useCallback(async () => {
    const validationPromises = Object.keys(data).map(async (field) => {
      const key = field as keyof T;
      return await validateField(key, data[key]);
    });

    const results = await Promise.all(validationPromises);
    return results.every(Boolean);
  }, [data, validateField]);

  const handleFieldChange = React.useCallback((field: keyof T, value: T[keyof T]) => {
    setData(prev => ({ ...prev, [field]: value }));
    
    if (touched[field]) {
      validateField(field, value);
    }
  }, [touched, validateField]);

  const handleFieldBlur = React.useCallback((field: keyof T) => {
    setTouched(prev => ({ ...prev, [field]: true }));
    validateField(field, data[field]);
  }, [data, validateField]);

  const reset = React.useCallback(() => {
    setData(initialData);
    setErrors({});
    setTouched({});
    setIsValidating(false);
  }, [initialData]);

  const isValid = Object.keys(errors).length === 0 && !isValidating;

  return {
    data,
    errors,
    touched,
    isValidating,
    isValid,
    setFieldValue: handleFieldChange,
    setFieldTouched: handleFieldBlur,
    validateField,
    validateForm,
    reset,
  };
};

/**
 * Common validation schemas
 */
export const validationSchemas = {
  login: {
    email: createValidator(
      validationRules.required('Email is required'),
      validationRules.email()
    ),
    password: createValidator(
      validationRules.required('Password is required')
    ),
  },

  register: {
    name: createValidator(
      validationRules.required('Name is required'),
      validationRules.minLength(2, 'Name must be at least 2 characters')
    ),
    email: createValidator(
      validationRules.required('Email is required'),
      validationRules.email()
    ),
    password: createValidator(
      validationRules.required('Password is required'),
      validationRules.password()
    ),
    confirmPassword: (password: string) => createValidator(
      validationRules.required('Please confirm your password'),
      validationRules.confirmPassword(password)
    ),
  },

  profile: {
    name: createValidator(
      validationRules.required('Name is required'),
      validationRules.minLength(2)
    ),
    email: createValidator(
      validationRules.required('Email is required'),
      validationRules.email()
    ),
    phone: createValidator(
      validationRules.phone()
    ),
  },

  course: {
    title: createValidator(
      validationRules.required('Course title is required'),
      validationRules.minLength(3, 'Title must be at least 3 characters'),
      validationRules.maxLength(100, 'Title must not exceed 100 characters')
    ),
    description: createValidator(
      validationRules.required('Description is required'),
      validationRules.minLength(10, 'Description must be at least 10 characters'),
      validationRules.maxLength(500, 'Description must not exceed 500 characters')
    ),
    difficulty: createValidator(
      validationRules.required('Difficulty level is required')
    ),
  },
} as const;

import React from 'react';