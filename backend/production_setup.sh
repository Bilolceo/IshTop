#!/bin/bash

# PRODUCTION SETUP HELPER SCRIPT
# Run this to complete your production configuration

echo "🚀 SmartCareer AI Production Setup Helper"
echo "=========================================="

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo "❌ .env.production not found!"
    echo "Run: cp .env.production.template .env.production"
    exit 1
fi

echo "✅ Production environment file found"

# Function to update config
update_config() {
    local key=$1
    local value=$2
    local description=$3
    
    echo ""
    echo "🔧 Configure $description"
    echo "Current: $(grep "^$key=" .env.production | cut -d'=' -f2-)"
    read -p "Enter new $description (or press Enter to keep current): " new_value
    
    if [ ! -z "$new_value" ]; then
        # Escape special characters in sed
        escaped_value=$(printf '%s\n' "$new_value" | sed 's/[[\.*^$()+?{|]/\\&/g')
        sed -i "s|^$key=.*|$key=$escaped_value|" .env.production
        echo "✅ Updated $key"
    else
        echo "⏭️  Kept current value"
    fi
}

# Database
update_config "DATABASE_URL" "PostgreSQL production database URL"

# API Keys
update_config "OPENAI_API_KEY" "OpenAI API key (from https://platform.openai.com/api-keys)"
update_config "GEMINI_API_KEY" "Gemini API key (from https://ai.google.dev/)"
update_config "STRIPE_SECRET_KEY" "Stripe secret key (from https://dashboard.stripe.com/apikeys)"

# Email
update_config "SMTP_USER" "Gmail address for SMTP"
update_config "SMTP_PASSWORD" "Gmail App Password (16 characters)"

# Redis (optional)
update_config "REDIS_URL" "Redis URL (optional)"

# Domain
update_config "FRONTEND_URL" "Your production domain (https://yourdomain.com)"
update_config "CORS_ORIGINS" "CORS origins (comma-separated)"
update_config "SMTP_FROM_EMAIL" "From email address (noreply@yourdomain.com)"

echo ""
echo "🎉 Production configuration updated!"
echo ""
echo "📋 Final checklist:"
echo "✅ Secure keys generated"
echo "🔧 API keys configured"  
echo "🗄️  Database URL set"
echo "📧 Email configured"
echo "🌐 Domain settings configured"
echo ""
echo "🚀 Ready to deploy!"
echo ""
echo "Test your configuration:"
echo "python -c \"from app.main import app; print('✅ Config loaded')\""
