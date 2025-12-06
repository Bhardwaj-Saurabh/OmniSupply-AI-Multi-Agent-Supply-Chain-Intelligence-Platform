#!/bin/bash
# Setup local PostgreSQL for OmniSupply

echo "=========================================="
echo "  OmniSupply - Local PostgreSQL Setup"
echo "=========================================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker first:"
    echo "   https://www.docker.com/products/docker-desktop"
    exit 1
fi

echo "✅ Docker found"

# Check if container already exists
if docker ps -a --format '{{.Names}}' | grep -q '^omnisupply-postgres$'; then
    echo "⚠️  Container 'omnisupply-postgres' already exists"
    read -p "Do you want to remove it and create fresh? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🗑️  Removing old container..."
        docker stop omnisupply-postgres 2>/dev/null
        docker rm omnisupply-postgres 2>/dev/null
    else
        echo "Starting existing container..."
        docker start omnisupply-postgres
        echo "✅ PostgreSQL is running!"
        exit 0
    fi
fi

# Create new PostgreSQL container
echo "🐳 Creating PostgreSQL container..."
docker run --name omnisupply-postgres \
  -e POSTGRES_USER=omnisupply \
  -e POSTGRES_PASSWORD=omnisupply123 \
  -e POSTGRES_DB=omnisupply \
  -p 5432:5432 \
  -d postgres:15

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to start..."
sleep 3

# Test connection
if docker exec omnisupply-postgres pg_isready -U omnisupply > /dev/null 2>&1; then
    echo "✅ PostgreSQL is ready!"
else
    echo "⚠️  PostgreSQL is starting... (this may take a few more seconds)"
    sleep 3
fi

echo ""
echo "=========================================="
echo "  ✅ Setup Complete!"
echo "=========================================="
echo ""
echo "📝 Next steps:"
echo ""
echo "1. Update your .env file with these values:"
echo ""
echo "   POSTGRES_USER=omnisupply"
echo "   POSTGRES_PASSWORD=omnisupply123"
echo "   POSTGRES_DB=omnisupply"
echo "   POSTGRES_HOST=localhost"
echo "   POSTGRES_PORT=5432"
echo ""
echo "2. Run the demo:"
echo "   python quick_demo_small_data.py"
echo ""
echo "📊 Container management:"
echo "   Start:  docker start omnisupply-postgres"
echo "   Stop:   docker stop omnisupply-postgres"
echo "   Remove: docker rm -f omnisupply-postgres"
echo "   Logs:   docker logs omnisupply-postgres"
echo ""
