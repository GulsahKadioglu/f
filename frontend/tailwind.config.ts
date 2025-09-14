/**
 * tailwind.config.ts
 *
 * This file configures Tailwind CSS for the Next.js project.
 * It defines the paths to the template files where Tailwind should scan for classes,
 * extends the default Tailwind theme with custom styles, and includes any custom plugins.
 *
 * Purpose:
 * - To customize Tailwind CSS to fit the specific design requirements of the application.
 * - To define where Tailwind should look for class names to generate the final CSS bundle.
 * - To extend Tailwind's default utility classes with project-specific values (e.g., colors, fonts, spacing).
 * - To integrate Tailwind plugins for additional functionality.
 *
 * Key Sections:
 * - `content`: Specifies the files that Tailwind CSS should scan for class names.
 *              This is crucial for optimizing the final CSS output by only including
 *              used utility classes.
 * - `theme.extend`: Allows extending Tailwind's default theme with custom values
 *                   without overwriting the entire default theme. This is where
 *                   custom colors, fonts, spacing, etc., are defined.
 * - `plugins`: An array to include official or third-party Tailwind CSS plugins
 *              that add new utility classes or functionalities.
 *
 * Note:
 * - This configuration is essential for Tailwind CSS to work correctly within the project.
 * - For more details on Tailwind CSS configuration, refer to the official documentation:
 *   https://tailwindcss.com/docs/configuration
 */

import { Config } from "tailwindcss";

const config = {
  // Specify the files where Tailwind should look for utility classes.
  // This helps Tailwind generate only the CSS that is actually used in your project,
  // leading to smaller CSS bundle sizes.
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
    "./node_modules/@nextui-org/theme/dist/**/*.{js,ts,jsx,tsx}",
  ],
  // Extend the default Tailwind theme with custom configurations.
  theme: {
    extend: {
      // Define custom background images.
      backgroundImage: {
        "gradient-radial": "radial-gradient(var(--tw-gradient-stops))",
        "gradient-conic":
          "conic-gradient(from 180deg at 50% 50%, var(--tw-gradient-stops))",
      },
    },
  },
  // Configure dark mode. 'class' strategy allows toggling dark mode by adding/removing a class (e.g., 'dark') to the HTML element.
  darkMode: "class",
  // Add Tailwind CSS plugins.
  // Plugins extend Tailwind's functionality with new features or utility classes.
  plugins: [],
};
export default config;
