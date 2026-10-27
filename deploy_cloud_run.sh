#!/bin/bash
# deploy_cloud_run.sh - One-command deployment script to Google Cloud Run

set -e

PROJECT_ID=${1:-"codeshift-ai-migration"}
REGION=${2:-"us-central1"}
SERVICE_NAME="codeshift-dashboard"

echo "=================================================================="
echo " Deploying CodeShift to Google Cloud Run (Project: $PROJECT_ID)"
echo "=================================================================="

# Set GCP project
gcloud config set project "$PROJECT_ID"

# Build and submit image to Google Artifact Registry / Google Container Registry
echo "[1/3] Building container image with Google Cloud Build..."
gcloud builds submit --tag "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest"

# Deploy container image to Cloud Run
echo "[2/3] Deploying container image to Cloud Run service..."
gcloud run deploy "$SERVICE_NAME" \
  --image "gcr.io/$PROJECT_ID/$SERVICE_NAME:latest" \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --port 8080 \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300

# Fetch deployed service URL
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --platform managed --region "$REGION" --format 'value(status.url)')

echo "[3/3] Deployment Successful!"
echo "Service is live at: $SERVICE_URL"
echo "Health Endpoint:    $SERVICE_URL/health"
echo "=================================================================="
