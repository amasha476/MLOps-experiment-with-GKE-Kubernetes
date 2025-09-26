# GCP Project Setup and Deployment Guide

## 1. Create GCP Project & Enable APIs

1. Create a new GCP project.
2. Enable the following APIs:
   - Kubernetes Engine API  
   - Google Container Registry API  
   - Compute Engine API  
   - IAM API  
   - Cloud Build API  
   - Cloud Storage API  

---

## 2. Networking & GKE Cluster

- Create a **GKE Cluster**.  
- Configure Networking → **Access using DNS**.  

---

## 3. Artifact Registry

- Create an **Artifact Registry** (format: Docker).  

---

## 4. Service Account & Roles

1. Create a **separate Service Account**.  
2. Assign the following roles:  
   - **Owner**  
   - **Storage Object Admin**  
   - **Storage Object Viewer**  
   - **Artifact Registry Administrator**  
   - **Artifact Registry Writer**  
3. Generate a **JSON key** for the Service Account.  

---

## 5. GitHub Secrets

Add the following secrets to your GitHub repository:  

- **GCP_PROJECT_ID** → your GCP project ID  
- **GCP_SA_KEY** → JSON service account key  

Path: `GitHub repo → Settings → Secrets and variables → Actions`

---

## 6. Docker & Kubernetes Setup

1. Add a `Dockerfile` for your ML app.  
2. Create Kubernetes manifests (e.g., `kubernetes-deployment.yaml`) and store them inside a folder like `k8s/`.  

---

## 7. GitHub Actions Workflow

Create a workflow file: `.github/workflows/deploy.yml`

```yaml
name: CI/CD Deployment to GKE

on:
    push:
        branches:
            - main

env:
    PROJECT_ID: ${{ secrets.GCP_PROJECT_ID }}
    GKE_CLUSTER: "<cluster_name>"
    GKE_REGION: "<region>"
    DEPLOYMENT_NAME: <deployment name>"
    REPOSITORY_NAME: "<GAR repo name>"
    IMAGE: "<path to image>"

jobs:
    build-and-deploy:
        runs-on: ubuntu-latest

        steps:
            - name: Checkout the Repository
              uses: actions/checkout@v2

            - name: Authenticate with Google Cloud Platform
              uses: google-github-actions/auth@v1
              with:
                credentials_json: ${{ secrets.GCP_SA_KEY }}

            - name: Configure the Google Cloud
              run: |
                gcloud config set project $PROJECT_ID
                gcloud auth configure-docker us-central1-docker.pkg.dev

            - name: Build and Push the Docker Image
              run: |
                docker build -t $IMAGE:$GITHUB_SHA .
                docker push $IMAGE:$GITHUB_SHA

            - name: GKE Configurations
              run: |
                gcloud container clusters get-credentials $GKE_CLUSTER --region $GKE_REGION --project $PROJECT_ID

            - name: Install gke-gcloud-auth-plugin
              run: |
                sudo apt-get update
                sudo apt-get install -y apt-transport-https ca-certificates gnupg
                echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
                curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
                sudo apt-get update
                sudo apt-get install -y google-cloud-cli-gke-gcloud-auth-plugin
                echo "USE_GKE_GCLOUD_AUTH_PLUGIN=True" >> $GITHUB_ENV

            - name: Final Deployment to GKE
              run: |
                kubectl apply -f kubernetes-deployment.yaml
                kubectl set image deployment/$DEPLOYMENT_NAME $DEPLOYMENT_NAME=$IMAGE:$GITHUB_SHA
