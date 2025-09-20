/**
 * next.config.mjs
 *
 * This file contains the configuration for the Next.js application.
 * It allows customization of various aspects of the Next.js build process,
 * such as routing, webpack configuration, environment variables, and more.
 *
 * Purpose:
 * - To configure the Next.js framework's behavior for the frontend application.
 * - To define custom settings that affect how the application is built, served, and optimized.
 *
 * Key Features:
 * - `nextConfig` object: The main configuration object where all Next.js settings are defined.
 * - JSDoc comments: Provide type hints and descriptions for better development experience.
 * - ES Module syntax (`.mjs`): Indicates that this file uses ES module syntax (`import`/`export`).
 *
 * Note:
 * - This file is automatically loaded by Next.js during development and build processes.
 * - For a comprehensive list of configuration options, refer to the official Next.js documentation:
 *   https://nextjs.org/docs/pages/api-reference/next-config-js
 */

/** @type {import('next').NextConfig} */
const nextConfig = {
  // Add this to prevent test files from being treated as pages
  pageExtensions: ['ts', 'tsx', 'js', 'jsx', 'md', 'mdx'],
  // `outputFileTracingRoot` specifies the root directory for file tracing.
  // This is important for optimizing the build output and ensuring all necessary files are included.
  outputFileTracingRoot: 'C:\\Users\\gulsa\\federated-cancer-screening',
  // `transpilePackages` is an array of packages that should be transpiled by Next.js.
  // This is often used for monorepos or when using packages that are not pre-transpiled for Next.js.
  transpilePackages: [

    '@ohif/core',
    '@ohif/extension-cornerstone',
    '@ohif/extension-cornerstone-dicom-rt',
    '@ohif/extension-cornerstone-dicom-seg',
    '@ohif/extension-cornerstone-dicom-sr',
    '@ohif/extension-default',
    '@ohif/extension-dicom-microscopy',
    '@ohif/extension-dicom-pdf',
    '@ohif/extension-dicom-video',
    '@ohif/extension-test',
    '@ohif/extension-ultrasound-pleura-bline',
    '@ohif/i18n',
    '@ohif/mode-basic-dev-mode',
    '@ohif/mode-longitudinal',
    '@ohif/mode-microscopy',
    '@ohif/mode-test',
    '@ohif/mode-ultrasound-pleura-bline',
    '@ohif/ui',
    '@ohif/ui-next',
    '@cornerstonejs/core',
    '@cornerstonejs/tools',
    '@cornerstonejs/codec-charls',
    '@cornerstonejs/codec-libjpeg-turbo-8bit',
    '@cornerstonejs/codec-openjpeg',
    '@cornerstonejs/codec-openjph',
    '@cornerstonejs/dicom-image-loader',
  ],
  eslint: {
    ignoreDuringBuilds: true,
  },
  webpack: (config, { isServer }) => {
    config.resolve.alias = {
      ...config.resolve.alias,
      '@cornerstonejs/tools': '@cornerstonejs/tools/src/index.ts',
      '@ohif/core': '@ohif/core/src/index.ts',
      '@ohif/extension-default': '@ohif/extension-default/src/index.ts',
      '@ohif/extension-dicom-microscopy': '@ohif/extension-dicom-microscopy/src/index.ts',
      '@ohif/extension-dicom-pdf': '@ohif/extension-dicom-pdf/src/index.ts',
      '@ohif/extension-dicom-video': '@ohif/extension-dicom-video/src/index.ts',
      '@ohif/ui-next': '@ohif/ui-next/src/index.ts',
    };
    return config;
  },
};

export default nextConfig;