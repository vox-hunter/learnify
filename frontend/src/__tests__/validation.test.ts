/**
 * @jest-environment jsdom
 */

import { describe, it, expect } from '@jest/globals';
import {
  validationRules,
  createValidator,
  validateForm,
  type FieldValidators,
} from '../utils/validation';

describe('Validation Utilities', () => {
  describe('validationRules', () => {
    describe('required', () => {
      const rule = validationRules.required();

      it('should pass for non-empty strings', () => {
        expect(rule.test('hello')).toBe(true);
      });

      it('should fail for empty strings', () => {
        expect(rule.test('')).toBe(false);
        expect(rule.test('   ')).toBe(false);
      });

      it('should fail for null/undefined', () => {
        expect(rule.test(null)).toBe(false);
        expect(rule.test(undefined)).toBe(false);
      });

      it('should pass for non-empty arrays', () => {
        expect(rule.test([1, 2, 3])).toBe(true);
      });

      it('should fail for empty arrays', () => {
        expect(rule.test([])).toBe(false);
      });
    });

    describe('email', () => {
      const rule = validationRules.email();

      it('should pass for valid emails', () => {
        expect(rule.test('test@example.com')).toBe(true);
        expect(rule.test('user.name@domain.co.uk')).toBe(true);
      });

      it('should fail for invalid emails', () => {
        expect(rule.test('invalid-email')).toBe(false);
        expect(rule.test('test@')).toBe(false);
        expect(rule.test('@example.com')).toBe(false);
      });

      it('should pass for empty values', () => {
        expect(rule.test('')).toBe(true);
        expect(rule.test(undefined as unknown as string)).toBe(true);
      });
    });

    describe('minLength', () => {
      const rule = validationRules.minLength(5);

      it('should pass for strings meeting minimum length', () => {
        expect(rule.test('hello')).toBe(true);
        expect(rule.test('hello world')).toBe(true);
      });

      it('should fail for strings below minimum length', () => {
        expect(rule.test('hi')).toBe(false);
        expect(rule.test('test')).toBe(false);
      });

      it('should pass for empty values', () => {
        expect(rule.test('')).toBe(true);
      });
    });

    describe('password', () => {
      const rule = validationRules.password();

      it('should pass for strong passwords', () => {
        expect(rule.test('StrongPass123!')).toBe(true);
        expect(rule.test('MySecure@Password2023')).toBe(true);
      });

      it('should fail for weak passwords', () => {
        expect(rule.test('weak')).toBe(false);
        expect(rule.test('password123')).toBe(false); // no uppercase or special
        expect(rule.test('PASSWORD123!')).toBe(false); // no lowercase
        expect(rule.test('StrongPassword!')).toBe(false); // no number
      });
    });

    describe('confirmPassword', () => {
      const originalPassword = 'MyPassword123!';
      const rule = validationRules.confirmPassword(originalPassword);

      it('should pass for matching passwords', () => {
        expect(rule.test('MyPassword123!')).toBe(true);
      });

      it('should fail for non-matching passwords', () => {
        expect(rule.test('DifferentPassword123!')).toBe(false);
      });
    });

    describe('number', () => {
      const rule = validationRules.number();

      it('should pass for valid numbers', () => {
        expect(rule.test('123')).toBe(true);
        expect(rule.test('123.45')).toBe(true);
        expect(rule.test('-123')).toBe(true);
      });

      it('should fail for non-numbers', () => {
        expect(rule.test('abc')).toBe(false);
        expect(rule.test('12abc')).toBe(false);
      });

      it('should pass for empty values', () => {
        expect(rule.test('')).toBe(true);
      });
    });
  });

  describe('createValidator', () => {
    it('should combine multiple rules', () => {
      const validator = createValidator(
        validationRules.required('Field is required'),
        validationRules.minLength(3, 'Too short'),
        validationRules.email('Invalid email')
      );

      // Valid email
      const validResult = validator('test@example.com');
      expect(validResult.isValid).toBe(true);
      expect(validResult.errors).toEqual([]);

      // Invalid: empty
      const emptyResult = validator('');
      expect(emptyResult.isValid).toBe(false);
      expect(emptyResult.errors).toContain('Field is required');

      // Invalid: too short
      const shortResult = validator('hi');
      expect(shortResult.isValid).toBe(false);
      expect(shortResult.errors).toContain('Too short');

      // Invalid: not an email
      const invalidEmailResult = validator('hello');
      expect(invalidEmailResult.isValid).toBe(false);
      expect(invalidEmailResult.errors).toContain('Invalid email');
    });
  });

  describe('validateForm', () => {
    interface TestForm extends Record<string, unknown> {
      name: string;
      email: string;
      age: string;
    }

    const validators = {
      name: createValidator(
        validationRules.required('Name is required'),
        validationRules.minLength(2)
      ),
      email: createValidator(
        validationRules.required('Email is required'),
        validationRules.email()
      ),
      age: createValidator(
        validationRules.number(),
        validationRules.positive()
      ),
    } as FieldValidators<TestForm>;

    it('should validate valid form data', () => {
      const formData: TestForm = {
        name: 'John Doe',
        email: 'john@example.com',
        age: '25',
      };

      const result = validateForm(formData, validators);
      expect(result.isValid).toBe(true);
      expect(result.errors).toEqual({});
    });

    it('should return errors for invalid form data', () => {
      const formData: TestForm = {
        name: '',
        email: 'invalid-email',
        age: 'abc',
      };

      const result = validateForm(formData, validators);
      expect(result.isValid).toBe(false);
      expect(result.errors.name).toContain('Name is required');
      expect(result.errors.email).toContain('Invalid email address');
      expect(result.errors.age).toContain('Must be a valid number');
    });
  });
});

// Test file types for file validation
const createMockFile = (name: string, size: number, type: string): File => {
  const file = new File([''], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('File Validation', () => {
  describe('fileSize', () => {
    const rule = validationRules.fileSize(1); // 1MB limit

    it('should pass for files under size limit', () => {
      const smallFile = createMockFile('small.txt', 500 * 1024, 'text/plain'); // 500KB
      expect(rule.test(smallFile)).toBe(true);
    });

    it('should fail for files over size limit', () => {
      const largeFile = createMockFile('large.txt', 2 * 1024 * 1024, 'text/plain'); // 2MB
      expect(rule.test(largeFile)).toBe(false);
    });

    it('should pass for no file', () => {
      expect(rule.test(null as unknown as File)).toBe(true);
    });
  });

  describe('fileType', () => {
    const rule = validationRules.fileType(['image/jpeg', 'image/png']);

    it('should pass for allowed file types', () => {
      const jpegFile = createMockFile('image.jpg', 1024, 'image/jpeg');
      const pngFile = createMockFile('image.png', 1024, 'image/png');
      expect(rule.test(jpegFile)).toBe(true);
      expect(rule.test(pngFile)).toBe(true);
    });

    it('should fail for disallowed file types', () => {
      const txtFile = createMockFile('document.txt', 1024, 'text/plain');
      expect(rule.test(txtFile)).toBe(false);
    });
  });
});