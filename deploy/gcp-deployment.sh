#!/bin/bash

# =============================================================================
# Journal Craft Crew - Google Cloud Platform Deployment Script
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
PROJECT_ID="journal-crew-production"
REGION="us-central1"
SERVICE_NAME="journal-crew"

print_step() {
    echo -e "${BLUE}🔧 STEP $1: $2${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ️  $1${NC}"
}

# Step 1: Initialize Google Cloud
init_gcp() {
    print_step "1" "Initializing Google Cloud Platform"

    echo -e "${YELLOW}Please ensure you have: \n1. gcloud CLI installed \n2. Authenticated with 'gcloud auth login'\n3. Selected billing account${NC}"

    # Create project if it doesn't exist
    if ! gcloud projects describe $PROJECT_ID &>/dev/null; then
        gcloud projects create $PROJECT_ID --name="Journal Craft Crew"
        print_success "Created GCP project: $PROJECT_ID"
    fi

    # Set active project
    gcloud config set project $PROJECT_ID

    # Enable required APIs
    gcloud services enable cloudbuild.googleapis.com
    gcloud services enable run.googleapis.com
    gcloud services enable sql-component.googleapis.com
    gcloud services enable sqladmin.googleapis.com
    gcloud services enable redis.googleapis.com
    gcloud services enable storage.googleapis.com

    print_success "Enabled required Google Cloud APIs"
}

# Step 2: Setup Database
setup_database() {
    print_step "2" "Setting up Cloud SQL PostgreSQL"

    # Create Cloud SQL instance
    if ! gcloud sql instances describe journal-db --region=$REGION &>/dev/null; then
        gcloud sql instances create journal-db \
            --database-version=POSTGRES_15 \
            --tier=db-f1-micro \
            --region=$REGION \
            --storage-type=SSD \
            --storage-size=10GB \
            --backup-configuration="enabled=true,backup-start-time=02:00"

        print_success "Created Cloud SQL PostgreSQL instance"
    fi

    # Create database
    if ! gcloud sql databases list --instance=journal-db | grep -q "journal_platform"; then
        gcloud sql databases create journal_platform --instance=journal-db
        print_success "Created journal_platform database"
    fi

    # Get database connection string
    DB_CONNECTION=$(gcloud sql instances describe journal-db \
        --format='value(connectionName)')

    print_info "Database connection name: $DB_CONNECTION"
}

# Step 3: Setup Redis
setup_redis() {
    print_step "3" "Setting up Memorystore Redis"

    # Create Redis instance
    if ! gcloud redis instances describe journal-redis \
        --region=$REGION &>/dev/null; then
        gcloud redis instances create journal-redis \
            --region=$REGION \
            --tier=STANDARD_HA \
            --size=1 \
            --redis-version=redis_7_2

        print_success "Created Memorystore Redis instance"
    fi

    # Get Redis host
    REDIS_HOST=$(gcloud redis instances describe journal-redis \
        --region=$REGION \
        --format='value(host)')

    print_info "Redis host: $REDIS_HOST"
}

# Step 4: Setup Cloud Storage
setup_storage() {
    print_step "4" "Setting up Cloud Storage"

    # Create storage bucket
    if ! gsutil ls | grep -q "gs://$PROJECT_ID-journal-files"; then
        gsutil mb -l $REGION gs://$PROJECT_ID-journal-files
        print_success "Created Cloud Storage bucket"
    fi
}

# Step 5: Deploy Backend
deploy_backend() {
    print_step "5" "Deploying Backend to Cloud Run"

    cd journal-platform-backend

    # Build and deploy using Cloud Build
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/journal-backend \
        --timeout=600s

    # Deploy to Cloud Run
    gcloud run deploy journal-backend \
        --image gcr.io/$PROJECT_ID/journal-backend \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 100 \
        --set-env-vars "DATABASE_URL=postgresql+asyncpg://user:password@/$DB_CONNECTION/journal_platform" \
        --set-env-vars "REDIS_URL=redis://$REDIS_HOST:6379/0" \
        --set-env-vars "OPENAI_API_KEY=\$OPENAI_API_KEY" \
        --set-cloud-secrets "OPENAI_API_KEY=OPENAI_API_KEY"

    print_success "Backend deployed to Cloud Run"
}

# Step 6: Deploy Frontend
deploy_frontend() {
    print_step "6" "Deploying Frontend to Cloud Run"

    cd journal-platform-frontend

    # Build and deploy frontend
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/journal-frontend \
        --timeout=600s

    # Deploy to Cloud Run
    gcloud run deploy journal-frontend \
        --image gcr.io/$PROJECT_ID/journal-frontend \
        --region $REGION \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --max-instances 100 \
        --set-env-vars "VITE_API_URL=\$BACKEND_URL"

    print_success "Frontend deployed to Cloud Run"
}

# Step 7: Setup DNS and SSL (optional)
setup_dns() {
    print_step "7" "Setting up DNS and SSL (Manual Step)"

    # Get service URLs
    BACKEND_URL=$(gcloud run services describe journal-backend \
        --region=$REGION \
        --format='value(status.url)')

    FRONTEND_URL=$(gcloud run services describe journal-frontend \
        --region=$REGION \
        --format='value(status.url)')

    print_info "Backend URL: $BACKEND_URL"
    print_info "Frontend URL: $FRONTEND_URL"

    print_info "To use custom domain:"
    print_info "1. Go to: https://console.cloud.google.com/run/domains"
    print_info "2. Add your custom domain"
    print_info "3. Update DNS records"
    print_info "4. SSL certificates will be provisioned automatically"
}

# Main execution
main() {
    print_step "START" "Google Cloud Platform Deployment for Journal Craft Crew"

    init_gcp
    setup_database
    setup_redis
    setup_storage
    deploy_backend
    deploy_frontend
    setup_dns

    print_success "🎉 Deployment completed successfully!"

    echo -e "${GREEN}Your Journal Craft Crew platform is now live on Google Cloud!${NC}"
    echo -e "${YELLOW}Next steps:"
    echo -e "1. Set your OPENAI_API_KEY in Google Secret Manager"
    echo -e "2. Configure custom domain if desired"
    echo -e "3. Monitor deployment in Cloud Console"
    echo -e "4. Set up billing alerts${NC}"
}

# Run main function
main "$@"