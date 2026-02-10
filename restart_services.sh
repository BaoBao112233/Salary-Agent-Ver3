#!/bin/bash
# Script để restart Docker services với cấu hình mới

echo "========================================="
echo "Restarting Salary Agent Services"
echo "========================================="

# Stop all services
echo -e "\n[1/4] Stopping services..."
sudo docker compose down

# Rebuild the application (nếu có thay đổi code)
echo -e "\n[2/4] Rebuilding application..."
sudo docker compose build salary-agent-service

# Start all services
echo -e "\n[3/4] Starting services with new configuration..."
sudo docker compose up -d

# Wait for services to be ready
echo -e "\n[4/4] Waiting for services to be ready..."
sleep 5

# Check services status
echo -e "\n========================================="
echo "Services Status:"
echo "========================================="
sudo docker compose ps

# Check logs
echo -e "\n========================================="
echo "Recent Logs (Salary Agent):"
echo "========================================="
sudo docker compose logs --tail=20 salary-agent-service

echo -e "\n========================================="
echo "Recent Logs (Postgres):"
echo "========================================="
sudo docker compose logs --tail=10 postgres

echo -e "\n========================================="
echo "✅ Restart Complete!"
echo "========================================="
echo "API: http://localhost:8000"
echo "Docs: http://localhost:8000/docs"
echo "Health: http://localhost:8000/health"
echo ""
echo "To view logs: sudo docker compose logs -f salary-agent-service"
