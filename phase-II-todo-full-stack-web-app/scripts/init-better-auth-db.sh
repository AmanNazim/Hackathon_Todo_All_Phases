#!/bin/bash
# Better Auth Database Migration Script
# This script initializes the Better Auth database tables

echo "🔄 Initializing Better Auth database..."

# Check if DATABASE_URL is set
if [ -z "$DATABASE_URL" ]; then
    echo "❌ Error: DATABASE_URL environment variable is not set"
    echo "Please set DATABASE_URL in your .env file"
    exit 1
fi

# Run Better Auth migration
cd "$(dirname "$0")/../frontend"

echo "📦 Installing dependencies..."
npm install

echo "🗄️  Running Better Auth migration..."
npx better-auth migrate

echo "✅ Database migration completed successfully!"
echo ""
echo "Next steps:"
echo "1. Redeploy your Vercel frontend"
echo "2. Try registering a new user"
