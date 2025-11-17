# Stage 1: Build (Vite + Node.js)
FROM node:lts-alpine AS builder 

# Declare build argument and expose it to the build environment
ARG VITE_API_URL
ENV VITE_API_URL=$VITE_API_URL

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Stage 2: Production (Nginx)
FROM nginx:alpine

RUN rm -rf /usr/share/nginx/html/*
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# IMPORTANT NOTE ABOUT VITE_API_URL:
# ------------------------------------------------------------------------------
# In Vite-based projects, environment variables prefixed with VITE_ are injected
# at build time, not at runtime.
#
# Therefore, you cannot rely on a .env file inside the container like in the backend.
# Instead, the VITE_API_URL must be passed as a build argument (via --build-arg or
# docker-compose's args section).
#
# The value is embedded into the static files during `vite build`, so the frontend
# will not be able to reach the backend if the URL is incorrect at build time.
#
# Reference:
# https://vitejs.dev/guide/env-and-mode.html#env-files
