// This is the Jest configuration file for the Next.js frontend application.
// Jest is a JavaScript testing framework designed to ensure the correctness of any JavaScript codebase.

module.exports = {
  // `roots` specifies the root directory that Jest should scan for tests.
  roots: ['<rootDir>/src', '<rootDir>/pages'],

  // `testEnvironment` specifies the test environment that will be used for testing.
  // `jsdom` provides a browser-like environment for testing React components.
  testEnvironment: 'jsdom',

  // `moduleFileExtensions` is an array of file extensions that Jest should look for.
  moduleFileExtensions: ['ts', 'tsx', 'js', 'jsx', 'json', 'node'],

  // `collectCoverage` indicates whether Jest should collect coverage information during test execution.
  collectCoverage: true,

  // `coverageDirectory` specifies the directory where Jest should output coverage files.
  coverageDirectory: 'coverage',

  // `collectCoverageFrom` specifies an array of glob patterns indicating a set of files for which coverage information should be collected.
  collectCoverageFrom: ['src/**/*.{ts,tsx}', 'pages/**/*.{ts,tsx}', '!src/**/*.d.ts'],

  // `setupFilesAfterEnv` is a list of paths to modules that run some code to configure or set up the testing framework before each test file in the suite is executed.
  setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

  // `transformIgnorePatterns` is an array of regex patterns that Jest uses to skip transforming files.
  // This is often used to prevent Jest from transforming files in `node_modules` except for specific ones (like `axios` here).
  transformIgnorePatterns: ['/node_modules/(?!axios)/'],

  // `transform` is a map from regular expressions to paths to transformers.
  // It tells Jest how to process files that match certain patterns (e.g., TypeScript/JavaScript files).
  transform: {
    '^.+\.(t|j)sx?$': [
      '@swc/jest',
      {
        jsc: {
          transform: {
            react: {
              runtime: 'automatic', // Enables the new JSX transform, which doesn't require `import React from 'react';`
            },
          },
        },
      },
    ],
  },

  // `moduleNameMapper` is a map from regular expressions to module names that allow to stub out resources with a single module.
  // This is useful for mocking assets (like images) or setting up path aliases.
  moduleNameMapper: {
    '\.(jpg|jpeg|png|gif|webp|svg)$': '<rootDir>/__mocks__/fileMock.js', // Mocks image imports.
    '^@/components/(.*)$': '<rootDir>/src/components/$1', // Alias for components.
    '^@/services/(.*)$': '<rootDir>/src/services/$1', // Alias for services.
    '^@/store/(.*)$': '<rootDir>/src/store/$1', // Alias for store.
  },
};
