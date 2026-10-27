# CodeShift Cloud Platform Deployment Guide

This guide details step-by-step instructions to deploy the **CodeShift Multi-Agent Migration System** to the cloud, fulfilling **Requirement 11 (Deploy your project on a cloud platform)**.

---

## 🌐 Supported Cloud Deployment Targets

| Cloud Provider | Type | Blueprint / Config | URL Format |
|---|---|---|---|
| **Render** | Managed Web Service | [`render.yaml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/render.yaml) | `https://codeshift.onrender.com` |
| **Google Cloud Run** | Serverless Container | [`deploy_cloud_run.sh`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/deploy_cloud_run.sh) / `Dockerfile` | `https://codeshift-<hash>-uc.a.run.app` |
| **Railway / Fly.io** | Container App | `Dockerfile` & `docker-compose.yml` | `https://codeshift.up.railway.app` |
| **Self-Hosted VPS (AWS/Azure)** | Docker Compose | [`docker-compose.yml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/docker-compose.yml) | `http://<vps_ip>:8080` |

---

## 🚀 Option 1: 1-Click Deployment to Render (Recommended for Viva)

Render is free, automatically builds from GitHub repositories, and natively interprets [`render.yaml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/render.yaml).

### Steps:
1. **Push your repository to GitHub**:
   ```bash
   git add .
   git commit -m "feat: complete all 11 criteria and cloud deployment configuration"
   git push origin main
   ```
2. **Log into [Render](https://dashboard.render.com/)**:
   - Click **New +** -> **Blueprints**.
   - Select your GitHub repository (`job-agent` / `CodeShift`).
   - Render automatically reads [`render.yaml`](file:///c:/Users/Jitender%20singh/OneDrive/Desktop/CodeShift/render.yaml) and provisions:
     - Environment: Python 3.12
     - Build Command: `pip install -r requirements.txt && pip install javalang fastapi uvicorn jinja2 langfuse`
     - Start Command: `uvicorn src.web.dashboard:app --host 0.0.0.0 --port $PORT`
3. **Verify Deployment**:
   - Access `https://codeshift-multi-agent-dashboard.onrender.com/health` to confirm `{"status": "healthy"}`.
   - Open root URL `https://codeshift-multi-agent-dashboard.onrender.com/` to interact with the visual dashboard.

---

## ☁️ Option 2: Serverless Container on Google Cloud Run

Google Cloud Run runs the Docker container with automatic SSL, scaling, and DDoS protection.

### Prerequisites:
- Google Cloud SDK (`gcloud` CLI installed).
- Active GCP Project with Cloud Run and Cloud Build APIs enabled.

### Steps:
1. Run the automated deployment script:
   - **Linux / macOS**:
     ```bash
     chmod +x deploy_cloud_run.sh
     ./deploy_cloud_run.sh <YOUR_GCP_PROJECT_ID> us-central1
     ```
   - **Windows PowerShell**:
     ```powershell
     .\deploy_cloud_run.ps1 -ProjectId "<YOUR_GCP_PROJECT_ID>" -Region "us-central1"
     ```
2. The script outputs the live HTTPS URL for presentation.

---

## 🐳 Option 3: Containerized Docker Deployment

To build and run locally or on any cloud virtual machine (AWS EC2, DigitalOcean Droplet, Azure VM):

```bash
# Build and run container in detached mode
docker-compose up --build -d

# Check running status
docker ps

# Inspect logs
docker logs -f codeshift_migration_dashboard
```
Open **`http://localhost:8080`** in your browser.

---

## 🔍 Cloud Health Check & Observability Endpoints

Every cloud deploy exposes the following REST endpoints for auditability and monitoring:

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | `GET` | Health check for Cloud Load Balancers |
| `/api/status` | `GET` | Current migration pipeline status & state summary |
| `/api/metrics` | `GET` | End-to-end performance, latency, and cost metrics |
| `/api/traces` | `GET` | Langfuse / OpenTelemetry spans for audit provenance |
| `/api/a2a` | `GET` | A2A Protocol message exchange history between ADK and CrewAI |
