#!/bin/bash

echo "🚀 Starting WhatsApp Automation with VNC Browser Viewer..."

# Start Xvfb (virtual display)
echo "📺 Starting virtual display..."
Xvfb :99 -screen 0 1920x1080x24 &
sleep 3

# Start window manager
echo "🪟 Starting window manager..."
fluxbox &
sleep 2

# Start VNC server
echo "🔐 Starting VNC server..."
x11vnc -display :99 -forever -shared -rfbport 5900 -nopw &
sleep 2

# Start noVNC (web-based VNC client)
echo "🌐 Starting noVNC web viewer..."
/opt/novnc/utils/novnc_proxy --vnc localhost:5900 --listen 6080 &
sleep 3

echo "✅ VNC server started successfully!"
echo "📺 Browser viewer will be available at: http://localhost:6080/vnc.html"
echo "🎯 Main dashboard at: http://localhost:${PORT:-8080}"

# Start Flask app
echo "🚀 Starting Flask application..."
exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:app
