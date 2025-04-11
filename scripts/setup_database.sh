#!/bin/bash

# Exit on error
set -e

# Load environment variables
set -a
source .env
set +a

echo "Setting up database..."

# Create postgres user if it doesn't exist
createuser -s postgres || true

# Create database if it doesn't exist
createdb -O postgres adhd_calendar || true

echo "Database setup complete!"
