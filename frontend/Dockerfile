# Dockerfile for the frontend application (Next.js).
# This multi-stage Dockerfile optimizes the build process and the final image size
# for the Next.js frontend application.

# ---- deps stage ----
# This stage is responsible for installing all production and development dependencies.
# It uses a slim Node.js image to keep the base image small.
FROM node:20-slim AS deps

# Set the working directory inside the container.
WORKDIR /app

# Install system dependencies required for building certain npm packages (e.g., `lightningcss`).
# `ca-certificates`, `curl`, `git`, `python3`, `make`, `g++`, `pkg-config`, `libssl-dev`,
# `libfontconfig1`, `libc6-dev` are common build tools and libraries.
# `rm -rf /var/lib/apt/lists/*` cleans up the apt cache to reduce image size.
RUN apt-get update && apt-get install -y --no-install-recommends \
  ca-certificates \
  curl \
  git \
  python3 \
  make \
  g++ \
  pkg-config \
  libssl-dev \
  libfontconfig1 \
  libc6-dev \
  && rm -rf /var/lib/apt/lists/*

# Copy `package.json` and `yarn.lock` (if present) to leverage Docker's build cache.
# This ensures that `node_modules` is rebuilt only when dependencies change.
COPY package.json ./

# Install `patch-package` globally if needed for applying patches to node modules.
RUN npm install -g patch-package

# Install project dependencies using yarn.
# `yarn install` installs all dependencies listed in `package.json`.
# `yarn add lightningcss --ignore-scripts` adds `lightningcss` while ignoring its post-install scripts
# which might cause issues in a Docker build environment.
RUN yarn install --network-timeout 300000
RUN yarn add lightningcss --ignore-scripts


# ---- build stage ----
# This stage builds the Next.js application for production.
FROM node:20-slim AS build

# Set the working directory inside the container.
WORKDIR /app

# Copy `node_modules` from the `deps` stage.
COPY --from=deps /app/node_modules ./node_modules
# Copy `yarn.lock` from the `deps` stage.
COPY --from=deps /app/yarn.lock ./
# Copy the rest of the application code.
COPY . .

# Disable Next.js telemetry during the build process.
ENV NEXT_TELEMETRY_DISABLED=1
# Build the Next.js application for production.
RUN yarn build

# ---- run stage ----
# This stage creates the final, lightweight production image.
FROM node:20-slim AS run

# Set the working directory inside the container.
WORKDIR /app

# Set the Node.js environment to production.
ENV NODE_ENV=production

# Create a non-root user for security best practices.
# `addgroup --system --gid 1001 nodejs` creates a system group.
# `adduser --system --uid 1001 nodejs` creates a system user.
RUN addgroup --system --gid 1001 nodejs && adduser  --system --uid 1001 nodejs

# Copy necessary build artifacts from the `build` stage.
# These include the compiled Next.js application (`.next`) and static assets (`public`).
COPY --from=build /app/.next ./.next
COPY --from=build /app/public ./public
# Copy `package.json` and `yarn.lock` for `yarn start` command.
COPY --from=deps /app/package.json /app/yarn.lock ./

# (Optional) Copy `node_modules` to the runtime image.
# This is needed if your application requires `node_modules` at runtime (e.g., for server-side rendering).
COPY --from=deps /app/node_modules ./node_modules

# Switch to the non-root user.
USER nodejs

# Expose port 3000, which is the default port for Next.js applications.
EXPOSE 3000

# Define the command to run when the container starts.
# `yarn start` runs the Next.js production server.
CMD ["yarn","start"]