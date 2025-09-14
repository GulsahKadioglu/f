// This is the ESLint configuration file for the Next.js frontend application.
// ESLint is a static code analysis tool for identifying problematic patterns found in JavaScript code.
// It helps to enforce coding standards and best practices.

module.exports = {
  // `extends` specifies a set of configurations to inherit from.
  // `next/core-web-vitals` is a predefined configuration provided by Next.js
  // that includes rules for ensuring good Core Web Vitals performance.
  extends: 'next/core-web-vitals',
  rules: {
    '@next/next/no-html-link-for-pages': 'off',
    '@next/next/no-img-element': 'off',
  },
};
