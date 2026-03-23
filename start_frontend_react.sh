#!/bin/bash

cd "$(dirname "$0")/frontend-react"

echo "🚀 Starting React frontend..."
echo "📦 Installing dependencies if needed..."

npm install

echo "✅ Starting development server on http://localhost:5173"
npm run dev
