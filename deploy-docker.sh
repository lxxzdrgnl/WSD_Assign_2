#!/bin/bash

# Exit on error
set -e

# 1. Log in to GitHub Container Registry
# Note: GH_TOKEN and GH_USER must be set as environment variables on the server
# or passed in securely. For this script, we assume they are available.
echo "Logging in to GitHub Container Registry..."
echo $GH_TOKEN | docker login ghcr.io -u $GH_USER --password-stdin

# 2. Pull the latest Docker image
echo "Pulling latest Docker image..."
docker pull ghcr.io/lxxzdrgnl/wsd_assign_2:latest

# 3. Stop and restart services with Docker Compose
echo "Restarting services with Docker Compose..."
docker-compose down
docker-compose up -d --build

# 4. Clean up dangling Docker images
echo "Cleaning up old images..."
docker image prune -f

echo "Deployment finished successfully!"
