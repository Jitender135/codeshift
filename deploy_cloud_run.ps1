# deploy_cloud_run.ps1 - PowerShell script for Google Cloud Run deployment
param(
    [string]$ProjectId = "codeshift-ai-migration",
    [string]$Region = "us-central1",
    [string]$ServiceName = "codeshift-dashboard"
)

Write-Host "==================================================================" -ForegroundColor Cyan
Write-Host " Deploying CodeShift to Google Cloud Run (Project: $ProjectId)" -ForegroundColor Cyan
Write-Host "==================================================================" -ForegroundColor Cyan

# Set GCP project
gcloud config set project $ProjectId

# Build image
Write-Host "[1/3] Building container image with Google Cloud Build..." -ForegroundColor Yellow
gcloud builds submit --tag "gcr.io/$ProjectId/$ServiceName`:latest"

# Deploy to Cloud Run
Write-Host "[2/3] Deploying container image to Cloud Run service..." -ForegroundColor Yellow
gcloud run deploy $ServiceName `
  --image "gcr.io/$ProjectId/$ServiceName`:latest" `
  --platform managed `
  --region $Region `
  --allow-unauthenticated `
  --port 8080 `
  --memory 2Gi `
  --cpu 2 `
  --timeout 300

# Get URL
$ServiceUrl = gcloud run services describe $ServiceName --platform managed --region $Region --format 'value(status.url)'

Write-Host "[3/3] Deployment Successful!" -ForegroundColor Green
Write-Host "Service is live at: $ServiceUrl" -ForegroundColor Green
Write-Host "Health Endpoint:    $ServiceUrl/health" -ForegroundColor Green
Write-Host "==================================================================" -ForegroundColor Cyan
