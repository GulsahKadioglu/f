/**
 * babel.config.js
 *
 * This file configures Babel for the React Native application. Babel is a JavaScript
 * compiler that transforms modern JavaScript code into a backward-compatible version
 * that can be run in older environments or by specific platforms (like React Native).
 *
 * Purpose:
 * - To enable the use of modern JavaScript features (ES6+, JSX, TypeScript) in React Native.
 * - To integrate plugins and presets that are essential for React Native development.
 * - To configure specific plugins, such as `react-native-dotenv`, for loading environment variables.
 *
 * Key Configuration:
 * - `presets`: A set of Babel plugins that transform specific language features.
 *   - `babel-preset-expo`: Recommended preset for Expo projects, handling React Native
 *     and Expo-specific transformations.
 * - `plugins`: Individual Babel plugins.
 *   - `module:react-native-dotenv`: This plugin allows the application to load environment
 *     variables defined in a `.env` file into `process.env` at compile time. This is crucial
 *     for managing configuration (like API URLs) that varies between environments
 *     and should not be hardcoded or committed to version control.
 *     - `moduleName`: The name under which environment variables will be imported (e.g., `@env`).
 *     - `path`: The path to the `.env` file.
 *     - `blacklist`, `whitelist`: Control which variables are included/excluded.
 *     - `safe`, `allowUndefined`: Control strictness of variable definition.
 *
 * Note:
 * - This file is automatically picked up by Metro (React Native's JavaScript bundler).
 * - Any changes to this file require restarting the Metro bundler.
 */

module.exports = function (api) {
  // `api.cache(true)` enables caching of Babel configurations.
  // This speeds up subsequent Babel compilations.
  api.cache(true);
  return {
    // `presets` define a set of transformations to apply.
    presets: ["babel-preset-expo"],
    // `plugins` define individual transformations.
    plugins: [
      [
        "module:react-native-dotenv",
        {
          // `moduleName` specifies the name under which environment variables will be imported.
          moduleName: "@env",
          // `path` specifies the path to the .env file.
          path: ".env",
          // `blacklist` specifies environment variables to exclude from loading.
          blacklist: null,
          // `whitelist` specifies environment variables to include for loading.
          whitelist: null,
          // `safe: false` allows the app to build even if the .env file is missing.
          safe: false,
          // `allowUndefined: true` allows environment variables to be undefined without throwing an error.
          allowUndefined: true,
        },
      ],
      // 'react-native-reanimated/plugin', // Required for react-native-reanimated
    ],
  };
};