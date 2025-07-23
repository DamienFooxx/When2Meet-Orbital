# Script to run Django migrations for Orbital When2Meet
# Project: orbitalwhen2meet-test
# This is only for google cloud run deployment

set -e  # Exit on any error

# Configuration variables
PROJECT_ID="orbitalwhen2meet-test"
REGION="asia-southeast1"
ARTIFACT_REGISTRY="asia-southeast1-docker.pkg.dev/orbitalwhen2meet-test/when2meet-repo"
IMAGE_NAME="orbital-when2meet-api"
INSTANCE_CONNECTION_NAME="orbitalwhen2meet-test:asia-southeast1:orbitalwhen2meet"
JOB_NAME="orbital-migrate-job"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Running Django migrations for Orbital When2Meet...${NC}"

# Check if job already exists
if gcloud run jobs describe $JOB_NAME --region=$REGION --project=$PROJECT_ID >/dev/null 2>&1; then
    echo -e "${YELLOW}Job '$JOB_NAME' already exists. Updating...${NC}"
    gcloud run jobs update $JOB_NAME \
        --image $ARTIFACT_REGISTRY/$IMAGE_NAME:latest \
        --region=$REGION \
        --project=$PROJECT_ID \
        --command="python" \
        --args="manage.py,migrate" \
        --set-env-vars "DB_NAME=when2meet" \
        --set-env-vars "DB_USER=admin" \
        --set-env-vars "DB_HOST=/cloudsql/$INSTANCE_CONNECTION_NAME" \
        --set-env-vars "DB_PORT=5432" \
        --set-secrets "SECRET_KEY=SECRET_KEY:latest" \
        --set-secrets "GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest" \
        --set-secrets "GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest" \
        --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
        --set-secrets "DB_PASSWORD=DB_PASSWORD:latest" \
        --set-cloudsql-instances $INSTANCE_CONNECTION_NAME \
        --memory 1Gi \
        --cpu 1
else
    echo -e "${YELLOW}Creating new migration job '$JOB_NAME'...${NC}"
    gcloud run jobs create $JOB_NAME \
        --image $ARTIFACT_REGISTRY/$IMAGE_NAME:latest \
        --region=$REGION \
        --project=$PROJECT_ID \
        --command="python" \
        --args="manage.py,migrate" \
        --set-env-vars "DB_NAME=when2meet" \
        --set-env-vars "DB_USER=admin" \
        --set-env-vars "DB_HOST=/cloudsql/$INSTANCE_CONNECTION_NAME" \
        --set-env-vars "DB_PORT=5432" \
        --set-secrets "SECRET_KEY=SECRET_KEY:latest" \
        --set-secrets "GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest" \
        --set-secrets "GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest" \
        --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
        --set-secrets "DB_PASSWORD=DB_PASSWORD:latest" \
        --set-cloudsql-instances $INSTANCE_CONNECTION_NAME \
        --memory 1Gi \
        --cpu 1
fi

# Execute the migration job
echo -e "${YELLOW}Executing migration job...${NC}"
gcloud run jobs execute $JOB_NAME --region=$REGION --project=$PROJECT_ID

echo -e "${GREEN}Migration job completed!${NC}"
echo -e "${YELLOW}Check the job logs for any errors:${NC}"
echo -e "${YELLOW}   gcloud run jobs logs read $JOB_NAME --region=$REGION --project=$PROJECT_ID${NC}" 