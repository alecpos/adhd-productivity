module.exports = {
  root: true,
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
    'plugin:@typescript-eslint/recommended-requiring-type-checking',
    'plugin:jest/recommended',
    'plugin:jest/style',
    'plugin:testing-library/react',
    'plugin:eslint-comments/recommended'
  ],
  parser: '@typescript-eslint/parser',
  parserOptions: {
    project: './tsconfig.json',
    tsconfigRootDir: __dirname,
  },
  plugins: [
    '@typescript-eslint',
    'jest',
    'testing-library',
    'jest-dom',
    'eslint-comments'
  ],
  env: {
    node: true,
    jest: true,
    'jest/globals': true,
  },
  settings: {
    jest: {
      version: 29,
    },
  },
  overrides: [
    {
      files: ['**/__tests__/**/*.[jt]s?(x)', '**/?(*.)+(spec|test).[jt]s?(x)'],
      extends: ['plugin:jest/recommended'],
      rules: {
        'jest/no-disabled-tests': 'warn',
        'jest/no-focused-tests': 'error',
        'jest/no-identical-title': 'error',
        'jest/prefer-to-have-length': 'warn',
        'jest/valid-expect': 'error',
        'jest/expect-expect': 'error',
        'jest/no-test-prefixes': 'error',
        'jest/no-test-return-statement': 'error',
        'jest/prefer-strict-equal': 'error',
        'jest/no-conditional-expect': 'error',
        'testing-library/await-async-queries': 'error',
        'testing-library/no-await-sync-queries': 'error',
        'testing-library/no-container': 'error',
        'testing-library/no-debugging-utils': 'warn',
        'testing-library/no-dom-import': ['error', 'react'],
        'no-console': ['error', { allow: ['warn', 'error', 'debug'] }],
      },
    },
    {
      files: ['*.d.ts'],
      rules: {
        '@typescript-eslint/ban-types': 'off',
        '@typescript-eslint/no-unused-vars': 'off',
        'import/export': 'off',
        'eslint-comments/no-unused-disable': 'off'
      }
    }
  ],
  rules: {
    // Type Safety
    '@typescript-eslint/explicit-module-boundary-types': 'error',
    '@typescript-eslint/explicit-function-return-type': 'error',
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unsafe-assignment': 'error',
    '@typescript-eslint/no-unsafe-member-access': 'error',
    '@typescript-eslint/no-unsafe-call': 'error',
    '@typescript-eslint/no-unsafe-return': 'error',
    '@typescript-eslint/strict-boolean-expressions': ['error', {
      allowString: false,
      allowNumber: false,
      allowNullableObject: false,
      allowNullableBoolean: false,
      allowNullableString: false,
      allowNullableNumber: false,
      allowAny: false,
    }],
    '@typescript-eslint/prefer-nullish-coalescing': 'error',
    '@typescript-eslint/no-floating-promises': 'error',

    // Code Style
    '@typescript-eslint/no-unused-vars': ['error', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_',
      caughtErrorsIgnorePattern: '^_'
    }],
    'no-console': ['error', { allow: ['warn', 'error'] }],
    '@typescript-eslint/no-shadow': 'error',

    // Type Restrictions
    '@typescript-eslint/no-restricted-types': [
      'error',
      {
        types: {
          '{}': {
            message: 'Avoid using empty object types. Use Record<string, unknown> instead.',
            fixWith: 'Record<string, unknown>'
          },
          'Function': {
            message: 'Avoid using Function type. Use specific function types like () => void.',
            fixWith: '(...args: any[]) => unknown'
          }
        }
      }
    ],
    'eslint-comments/no-unused-disable': 'error'
  },
}; 