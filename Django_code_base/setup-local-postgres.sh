#!/bin/bash

set -e

DB_NAME="when2meet"
DB_USER="admin"
DB_PASS="orbital2425"

# Check for Homebrew
if ! command -v brew &> /dev/null; then
  echo "Homebrew not found. Please install Homebrew first: https://brew.sh/"
  exit 1
fi

echo "[1/4] Checking for PostgreSQL..."
if ! command -v psql &> /dev/null; then
  echo "PostgreSQL not found. Installing with Homebrew..."
  brew install postgresql
else
  echo "PostgreSQL is already installed."
fi

echo "[2/4] Starting PostgreSQL service..."
brew services start postgresql
sleep 2

echo "[3/4] Creating database and user..."
# Create user if not exists
echo "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" | psql postgres || true
# Create database if not exists
echo "CREATE DATABASE $DB_NAME OWNER $DB_USER;" | psql postgres || true
# Grant privileges
echo "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" | psql postgres || true

echo "[4/4] PostgreSQL setup complete!"
echo "\nUse the following settings in your Django .env or settings file:"
echo "----------------------------------------"
echo "ENGINE=django.db.backends.postgresql"
echo "NAME=$DB_NAME"
echo "USER=$DB_USER"
echo "PASSWORD=$DB_PASS"
echo "HOST=localhost"
echo "PORT=5432"
echo "----------------------------------------"

echo "You can now run migrations and start your Django backend!" 