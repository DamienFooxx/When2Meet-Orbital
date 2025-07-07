#!/bin/bash

# Script to set up database password secret for Orbital When2Meet deployment
# Project: orbitalwhen2meet-test
# Note: Other secrets (SECRET_KEY, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_API_KEY) 
# are already configured in Secret Manager

set -e  # Exit on any error

# Configuration variables
PROJECT_ID="orbitalwhen2meet-test"
REGION="asia-southeast1"
SERVICE_NAME="orbital-when2meet-api"
SECRET_NAME="orbital-db-password"
SERVICE_ACCOUNT="686579494898-compute@developer.gserviceaccount.com"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Setting up database password secret for Orbital When2Meet...${NC}"

# Check if secret already exists
if gcloud secrets describe $SECRET_NAME --project=$PROJECT_ID >/dev/null 2>&1; then
    echo -e "${YELLOW}Secret '$SECRET_NAME' already exists. Updating...${NC}"
else
    echo -e "${YELLOW}Creating new secret '$SECRET_NAME'...${NC}"
    gcloud secrets create $SECRET_NAME --project=$PROJECT_ID
fi

# Prompt for database password
echo -e "${YELLOW}Setting database password...${NC}"
DB_PASSWORD="orbital2425"

# Update the secret with the password
echo -e "${YELLOW}Updating secret with database password...${NC}"
echo -n "$DB_PASSWORD" | gcloud secrets versions add $SECRET_NAME --data-file=- --project=$PROJECT_ID

# Grant Cloud Run service account access to the secret
echo -e "${YELLOW}Granting Cloud Run access to secret...${NC}"
gcloud secrets add-iam-policy-binding $SECRET_NAME \
    --member="serviceAccount:$SERVICE_ACCOUNT" \
    --role="roles/secretmanager.secretAccessor" \
    --project=$PROJECT_ID

# Update Cloud Run service to use the secret
echo -e "${YELLOW}Updating Cloud Run service to use secret...${NC}"
gcloud run services update $SERVICE_NAME \
    --region=$REGION \
    --project=$PROJECT_ID \
    --set-secrets="DB_PASSWORD=$SECRET_NAME:latest"

echo -e "${GREEN}Database password secret setup completed successfully!${NC}"
echo -e "${YELLOW}All secrets are now configured:${NC}"
echo -e "${YELLOW}    SECRET_KEY (already configured)${NC}"
echo -e "${YELLOW}    GOOGLE_CLIENT_ID (already configured)${NC}"
echo -e "${YELLOW}    GOOGLE_CLIENT_SECRET (already configured)${NC}"
echo -e "${YELLOW}    GOOGLE_API_KEY (already configured)${NC}"
echo -e "${YELLOW}    DB_PASSWORD (just configured)${NC}"
echo -e "${YELLOW}Next step: Run Django migrations if needed${NC}" 