#!/bin/bash
echo "🧹 Fixing cache issues..."

# Kill old servers
pkill -f "http.server 8080"
sleep 1

# Restart fresh server
cd /home/cc/claude_code/gpt2chat/docs
python3 -m http.server 8080 > server.log 2>&1 &

sleep 2

# Verify
echo ""
echo "✅ Server restarted on port 8080"
echo "📊 Xenova models in HTML:" $(curl -s http://localhost:8080 | grep -c "Xenova/")
echo "🚫 onnx-community models:" $(curl -s http://localhost:8080 | grep -c "onnx-community" || echo "0")
echo ""
echo "🌐 Access webapp at:"
echo "   http://localhost:8080/clear_cache.html  (Clear cache first)"
echo "   http://localhost:8080/                   (Main app)"
echo ""
echo "💡 Or open in Incognito/Private mode for fresh session"
