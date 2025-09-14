/**
 * postcss.config.js
 *
 * This file configures PostCSS, a powerful tool for transforming CSS with JavaScript.
 * In this Next.js frontend application, it is primarily used to process CSS with
 * Tailwind CSS and Autoprefixer, ensuring modern CSS features are compatible
 * across different browsers.
 *
 * Purpose:
 * - To define PostCSS plugins that process CSS files during the build process.
 * - To integrate Tailwind CSS for utility-first styling.
 * - To automatically add vendor prefixes to CSS rules for broader browser compatibility.
 *
 * Key Components:
 * - `plugins` object: Contains a list of PostCSS plugins to be applied.
 * - `tailwindcss`: A PostCSS plugin that processes Tailwind CSS directives and generates
 *                  the necessary utility classes.
 * - `autoprefixer`: A PostCSS plugin that automatically adds vendor prefixes (e.g., `-webkit-`, `-moz-`)
 *                   to CSS rules, based on the `browserslist` configuration, ensuring
 *                   styles work across various browsers without manual prefixing.
 *
 * Note:
 * - This configuration is automatically picked up by Next.js when processing CSS.
 * - For more details on PostCSS and its plugins, refer to their respective documentation.
 */

module.exports = {
  plugins: {
    // Integrates Tailwind CSS with PostCSS.
    "@tailwindcss/postcss": {},
    // Adds vendor prefixes to CSS rules for cross-browser compatibility.
    autoprefixer: {},
  },
}
