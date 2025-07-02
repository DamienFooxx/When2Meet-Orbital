#!/bin/bash

# Health check script for Orbital When2Meet Cloud Run service
# Project: orbitalwhen2meet-test

set -e  # Exit on any error

# Configuration variables
PROJECT_ID="orbitalwhen2meet-test"
REGION="asia-southeast1"
SERVICE_NAME="orbital-when2meet-api"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running health check for Orbital When2Meet...${NC}"

# Get the service URL
echo -e "${YELLOW}Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

if [ -z "$SERVICE_URL" ]; then
    echo -e "${RED}Could not get service URL. Service might not be deployed.${NC}"
    exit 1
fi

echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"

# --- Health Checks ---
echo "Performing health checks..."

# Check Root endpoint
ROOT_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/")

# Check Admin endpoint
ADMIN_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/admin/")

# Check new Health endpoint
API_HEALTH_STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$SERVICE_URL/api/health/")

# --- Log Check ---
echo "Checking recent logs for errors..."
ERRORS=$(gcloud run services logs read "$SERVICE_NAME" --region "$REGION" --limit 50 --format="value(textPayload)" | grep -i -E "error|fail|critical|traceback" || true)

# --- Report ---
echo -e "\n--- Health Check Report ---"
HEALTHY=true

# Root endpoint check
if [ "$ROOT_STATUS" -eq 200 ]; then
  echo "Root endpoint: OK (HTTP $ROOT_STATUS)"
else
  echo "Root endpoint: FAILED (HTTP $ROOT_STATUS)"
  HEALTHY=false
fi

# Admin endpoint check
if [ "$ADMIN_STATUS" -eq 302 ]; then
  echo "Admin endpoint: OK, redirecting as expected (HTTP $ADMIN_STATUS)"
else
  echo "Admin endpoint: FAILED (HTTP $ADMIN_STATUS)"
  HEALTHY=false
fi

# API Health check
if [ "$API_HEALTH_STATUS" -eq 200 ]; then
  echo "API health endpoint: OK (HTTP $API_HEALTH_STATUS)"
else
  echo "API health endpoint: FAILED (HTTP $API_HEALTH_STATUS)"
  HEALTHY=false
fi

# Log check
if [ -z "$ERRORS" ]; then
  echo "Logs: No recent errors found."
else
  echo "Logs: Found potential errors in recent logs:"
  echo "$ERRORS"
  HEALTHY=false
fi

# Final verdict
echo "---"
if [ "$HEALTHY" = true ]; then
  echo "Service appears to be healthy."
  exit 0
else
  echo "Service appears to be unhealthy."
  exit 1
fi 