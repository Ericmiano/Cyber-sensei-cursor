#!/bin/bash
# Start Celery worker

set -e

echo "🔄 Starting Celery Worker..."

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found"
    exit 1
fi

source venv/bin/activate

echo "✅ Celery worker starting..."
echo "   Tasks will be processed from Redis queue"
echo ""
echo "Press Ctrl+C to stop"
echo ""

celery -A app.tasks.celery_app worker --loglevel=info
