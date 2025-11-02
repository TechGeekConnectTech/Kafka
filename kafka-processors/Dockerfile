# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    netcat-openbsd \
    procps \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create logs directory
RUN mkdir -p logs

# Make scripts executable
RUN chmod +x start_all.sh test_system.py

# Expose API port
EXPOSE 8082

# Create a startup script for Docker
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
echo "🐳 Starting Kafka Processors in Docker..."\n\
\n\
# Wait for Kafka to be ready\n\
if [ -n "$KAFKA_BOOTSTRAP_SERVERS" ]; then\n\
    echo "⏳ Waiting for Kafka to be ready..."\n\
    KAFKA_HOST_ONLY=$(echo ${KAFKA_BOOTSTRAP_SERVERS} | cut -d: -f1)\n\
    KAFKA_PORT_ONLY=$(echo ${KAFKA_BOOTSTRAP_SERVERS} | cut -d: -f2)\n\
    until timeout 5 nc -z ${KAFKA_HOST_ONLY} ${KAFKA_PORT_ONLY}; do\n\
        echo "📡 Kafka is unavailable - sleeping"\n\
        sleep 2\n\
    done\n\
    echo "✅ Kafka is ready!"\n\
fi\n\
\n\
# Create Kafka topics if they dont exist\n\
echo "📝 Setting up Kafka topics..."\n\
python3 -c "\n\
from kafka import KafkaAdminClient, KafkaProducer\n\
from kafka.admin import NewTopic\n\
import time\n\
import os\n\
\n\
bootstrap_servers = os.getenv('"'"'KAFKA_BOOTSTRAP_SERVERS'"'"', '"'"'localhost:9092'"'"').split('"'"','"'"')\n\
\n\
try:\n\
    admin = KafkaAdminClient(bootstrap_servers=bootstrap_servers)\n\
    topic = NewTopic(name='"'"'server-demise-pipeline'"'"', num_partitions=3, replication_factor=1)\n\
    admin.create_topics([topic])\n\
    print('"'"'✅ Topic created successfully'"'"')\n\
except Exception as e:\n\
    print(f'"'"'ℹ️  Topic may already exist: {e}'"'"')\n\
" || echo "⚠️  Could not create topics (they may already exist)"\n\
\n\
# Start processor manager in background\n\
echo "🚀 Starting processor manager..."\n\
python3 processor_manager_new.py &\n\
PROCESSOR_PID=$!\n\
\n\
# Function to handle shutdown\n\
cleanup() {\n\
    echo "🛑 Shutting down gracefully..."\n\
    kill $PROCESSOR_PID 2>/dev/null || true\n\
    wait $PROCESSOR_PID 2>/dev/null || true\n\
    exit 0\n\
}\n\
\n\
# Set up signal handlers\n\
trap cleanup SIGTERM SIGINT\n\
\n\
# Wait for processors to initialize\n\
sleep 8\n\
\n\
# Check if processor manager is still running\n\
if ! kill -0 $PROCESSOR_PID 2>/dev/null; then\n\
    echo "❌ Processor manager failed to start"\n\
    exit 1\n\
fi\n\
\n\
# Start API server\n\
echo "🌐 Starting API server on port 8082..."\n\
exec python3 -m uvicorn api.main:app --host 0.0.0.0 --port 8082 --reload\n\
' > /app/docker-start.sh && chmod +x /app/docker-start.sh

# Health check - check both API and processor health
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD curl -f http://localhost:8082/health && curl -f http://localhost:8082/health/processors || exit 1

# Default command
CMD ["/app/docker-start.sh"]