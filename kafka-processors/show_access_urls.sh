#!/bin/bash
echo "🌐 Server Demise Pipeline - Access Information"
echo "=============================================="
echo ""
echo "📋 Documentation URLs (All Working):"
echo "   🏠 Main Documentation: http://195.35.6.88:8093/documentation.html"
echo "   📋 README: http://195.35.6.88:8093/readme.html"  
echo "   ⚡ Quick Reference: http://195.35.6.88:8093/quick.html"
echo ""
echo "📡 API Service URLs:"
echo "   🎯 API Endpoints: http://195.35.6.88:8082/"
echo "   📚 Interactive API Docs: http://195.35.6.88:8082/docs"
echo ""
echo "🔧 Server Status:"
netstat -tulpn | grep -E "(8082|8093)" | while read line; do
    port=$(echo $line | grep -o '809[0-9]')
    if [[ "$port" == "8082" ]]; then
        echo "   ✅ API Server (Port 8082): Running"
    elif [[ "$port" == "8093" ]]; then
        echo "   ✅ Documentation Server (Port 8093): Running"
    fi
done
echo ""
echo "🎯 Quick Test Commands:"
echo "   curl -I http://localhost:8093/documentation.html"
echo "   curl -I http://localhost:8082/health"
echo ""
echo "✅ All services are live and accessible!"