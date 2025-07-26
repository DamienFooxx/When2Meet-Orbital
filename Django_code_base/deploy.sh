# Deployment script for Orbital When2Meet Django application
# Project: orbitalwhen2meet-test
# This is only for google cloud run deployment

set -e  # Exit on any error

# Configuration variables
PROJECT_ID="orbitalwhen2meet-test"
REGION="asia-southeast1"
ARTIFACT_REGISTRY="asia-southeast1-docker.pkg.dev/orbitalwhen2meet-test/when2meet-repo"
SERVICE_NAME="when2meet-backend"
IMAGE_NAME="when2meet-backend"
INSTANCE_CONNECTION_NAME="orbitalwhen2meet-test:asia-southeast1:orbitalwhen2meet"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting deployment for Orbital When2Meet...${NC}"

# Step 1: Navigate to Django Code Base directory (if not already there)
echo -e "${YELLOW}Checking current directory...${NC}"
if [ ! -f "manage.py" ]; then
    echo -e "${YELLOW}Navigating to Django Code Base directory...${NC}"
    cd "Django Code Base"
else
    echo -e "${GREEN}Already in Django Code Base directory${NC}"
fi

# Step 2: Configure Docker to use gcloud as a credential helper
echo -e "${YELLOW}Configuring Docker authentication...${NC}"
gcloud auth configure-docker asia-southeast1-docker.pkg.dev

# Step 3: Build the Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build --platform linux/amd64 -t $ARTIFACT_REGISTRY/$IMAGE_NAME:latest .

# Step 4: Push the image to Artifact Registry
echo -e "${YELLOW}Pushing image to Artifact Registry...${NC}"
docker push $ARTIFACT_REGISTRY/$IMAGE_NAME:latest

# Step 5: Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image $ARTIFACT_REGISTRY/$IMAGE_NAME:latest \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --add-cloudsql-instances $INSTANCE_CONNECTION_NAME \
    --set-env-vars "DB_NAME=when2meet" \
    --set-env-vars "DB_USER=admin" \
    --set-env-vars "DB_HOST=/cloudsql/$INSTANCE_CONNECTION_NAME" \
    --set-env-vars "DB_PORT=5432" \
    --set-secrets "SECRET_KEY=SECRET_KEY:latest" \
    --set-secrets "GOOGLE_CLIENT_ID=GOOGLE_CLIENT_ID:latest" \
    --set-secrets "GOOGLE_CLIENT_SECRET=GOOGLE_CLIENT_SECRET:latest" \
    --set-secrets "GOOGLE_API_KEY=GOOGLE_API_KEY:latest" \
    --memory 1Gi \
    --cpu 1 \
    --max-instances 10 \
    --min-instances 0 \
    --port 8080

# Step 6: Get the service URL
echo -e "${YELLOW}Getting service URL...${NC}"
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --project=$PROJECT_ID --format="value(status.url)")

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"
echo -e "${YELLOW}Remember to:${NC}"
echo -e "${YELLOW}   1. Set the DB_PASSWORD environment variable in Cloud Run${NC}"
echo -e "${YELLOW}   2. Run Django migrations if needed${NC}"

# Optional: Run migrations (uncomment if needed)
# echo -e "${YELLOW}Running database migrations...${NC}"
# gcloud run jobs create migrate-job \
#     --image $ARTIFACT_REGISTRY/$IMAGE_NAME:latest \
#     --region $REGION \
#     --project $PROJECT_ID \
#     --command="python" \
#     --args="manage.py,migrate" \
#     --set-env-vars "DB_NAME=when2meet" \
#     --set-env-vars "DB_USER=admin" \
#     --set-env-vars "DB_HOST=/cloudsql/$INSTANCE_CONNECTION_NAME" \
#     --set-env-vars "DB_PORT=5432" 