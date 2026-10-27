#!/bin/bash

echo "Starting VNC server for remote browser access..."

# Start Xvfb (virtual display)
Xvfb :99 -screen 0 1920x1080x24 &
sleep 2

# Start window manager
fluxbox &
sleep 1

# Start VNC server
x11vnc -display :99 -forever -shared -rfbport 5900 -passwd whatsapp &
sleep 2

# Start noVNC (web-based VNC client)
websockify --web=/usr/share/novnc 6080 localhost:5900 &
sleep 2

echo "✅ VNC server started!"
echo "📺 Browser viewer available at: http://localhost:6080/vnc.html"
echo "🔐 VNC Password: whatsapp"

# Start Flask app
exec gunicorn --bind :${PORT:-8080} --workers 1 --threads 8 --timeout 0 app:app
