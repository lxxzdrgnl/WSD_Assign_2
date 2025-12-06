#!/bin/bash

# Exit on error
set -e

echo "Starting deployment..."

# 1. Pull latest code from GitHub
echo "Pulling latest code..."
git pull origin main

# 2. Stop existing containers
echo "Stopping existing containers..."
docker-compose down || true

# 3. Build and start services with Docker Compose
echo "Building and starting services..."
docker-compose up -d --build

# 4. Wait for services to be ready
echo "Waiting for services to start..."
sleep 10

# 5. Check service status
echo "Checking service status..."
docker-compose ps

# 6. Clean up dangling Docker images
echo "Cleaning up old images..."
docker image prune -f

echo "Deployment finished successfully!"
