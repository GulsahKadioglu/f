// This is the ESLint configuration file for the React Native mobile application.
// ESLint is a static code analysis tool for identifying problematic patterns found in JavaScript and TypeScript code.
// It helps to enforce coding standards and best practices, especially in a React Native environment.

module.exports = {
  // `root: true` tells ESLint to stop looking for configuration files in parent directories.
  root: true,
  // Specifies the parser to be used by ESLint. `@typescript-eslint/parser` allows ESLint to parse TypeScript code.
  parser: "@typescript-eslint/parser",
  // Specifies the plugins to be used by ESLint. These plugins provide additional rules and functionalities.
  plugins: ["@typescript-eslint", "react", "react-native", "prettier"],
  // `extends` specifies a set of configurations to inherit from.
  // These are common recommended configurations for ESLint, React, TypeScript, and Prettier integration.
  extends: [
    "eslint:recommended",
    "plugin:react/recommended",
    "plugin:@typescript-eslint/recommended",
    "plugin:prettier/recommended",
  ],
  // `parserOptions` configure the parser.
  parserOptions: {
    // `ecmaFeatures.jsx: true` enables JSX parsing.
    ecmaFeatures: {
      jsx: true,
    },
    // `ecmaVersion: 2020` sets the ECMAScript version to 2020.
    ecmaVersion: 2020,
    // `sourceType: "module"` allows the use of ES modules.
    sourceType: "module",
  },
  // `rules` define specific ESLint rules to enable, disable, or configure.
  rules: {
    // Enforces Prettier formatting rules and reports differences as ESLint errors.
    "prettier/prettier": "error",
    // Disables the `prop-types` rule, as PropTypes are often replaced by TypeScript in modern React projects.
    "react/prop-types": "off",
    // Add any custom rules here if needed.
  },
  // `settings` provide shared settings for plugins.
  settings: {
    // Automatically detects the React version to be used by the `eslint-plugin-react`.
    react: {
      version: "detect",
    },
  },
  // `env` specifies the environments in which the code is expected to run.
  env: {
    // Enables React Native specific global variables and rules.
    "react-native/react-native": true,
  },
};