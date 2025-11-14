#!/bin/bash

# =============================================================================
# Journal Craft Crew - Google Cloud + Cloudflare Deployment Script
# =============================================================================

set -e

# Configuration
PROJECT_ID="journal-crew-production"
REGION="us-central1"
DOMAIN="journalcraftcrew.com"  # Replace with your domain

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_step() {
    echo -e "${BLUE}🔧 $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

# Step 1: Deploy backend for Cloudflare
deploy_backend_cloudflare() {
    print_step "Deploying Backend for Cloudflare Integration"

    cd journal-platform-backend

    # Build image
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/journal-backend

    # Deploy to Cloud Run with Cloudflare-specific settings
    gcloud run deploy journal-backend \
        --image gcr.io/$PROJECT_ID/journal-backend \
        --region $REGION \
        --allow-unauthenticated \
        --memory 512Mi \
        --cpu 1 \
        --max-instances 100 \
        --min-instances 0 \
        --set-env-vars "CORS_ORIGINS=https://$DOMAIN,https://www.$DOMAIN" \
        --set-env-vars "TRUSTED_HOSTS=$DOMAIN,www.$DOMAIN" \
        --set-cloud-secrets "OPENAI_API_KEY=OPENAI_API_KEY"

    print_success "Backend deployed for Cloudflare"
}

# Step 2: Deploy frontend for Cloudflare
deploy_frontend_cloudflare() {
    print_step "Deploying Frontend for Cloudflare Integration"

    cd journal-platform-frontend

    # Build with Cloudflare-specific config
    gcloud builds submit \
        --tag gcr.io/$PROJECT_ID/journal-frontend \
        --substitutions _API_URL="https://api.$DOMAIN"

    # Deploy to Cloud Run
    gcloud run deploy journal-frontend \
        --image gcr.io/$PROJECT_ID/journal-frontend \
        --region $REGION \
        --allow-unauthenticated \
        --memory 256Mi \
        --cpu 1 \
        --max-instances 100 \
        --min-instances 0

    print_success "Frontend deployed for Cloudflare"
}

# Step 3: Get Cloud Run URLs for Cloudflare setup
get_service_urls() {
    print_step "Getting Service URLs for Cloudflare Configuration"

    BACKEND_URL=$(gcloud run services describe journal-backend \
        --region=$REGION \
        --format='value(status.url)')

    FRONTEND_URL=$(gcloud run services describe journal-frontend \
        --region=$REGION \
        --format='value(status.url)')

    print_success "Service URLs obtained"
    echo -e "${YELLOW}Backend URL: $BACKEND_URL${NC}"
    echo -e "${YELLOW}Frontend URL: $FRONTEND_URL${NC}"

    # Save URLs to file for Cloudflare setup
    cat > cloudflare-urls.txt << EOF
Backend URL: $BACKEND_URL
Frontend URL: $FRONTEND_URL
Domain: $DOMAIN

Cloudflare DNS Records:
Type: A | Name: @ | Content: Use Cloudflare proxy
Type: A | Name: api | Content: Use Cloudflare proxy
Type: CNAME | Name: www | Content: $DOMAIN
EOF

    print_success "Cloudflare configuration saved to cloudflare-urls.txt"
}

# Main execution
main() {
    print_step "Google Cloud + Cloudflare Deployment Starting"

    deploy_backend_cloudflare
    deploy_frontend_cloudflare
    get_service_urls

    print_success "🎉 Google Cloud deployment completed!"
    echo -e "${YELLOW}Next steps:"
    echo -e "1. Setup Cloudflare using cloudflare-urls.txt"
    echo -e "2. Configure DNS records"
    echo -e "3. Test your application"
    echo -e "4. Enable Cloudflare caching${NC}"
}

main "$@"