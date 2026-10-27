# Use official Playwright image which has all dependencies pre-installed
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

# Install VNC server and noVNC for remote browser access
RUN apt-get update && apt-get install -y \
    x11vnc \
    xvfb \
    fluxbox \
    websockify \
    novnc \
    && rm -rf /var/lib/apt/lists/*

# Set up virtual display
ENV DISPLAY=:99
ENV RESOLUTION=1920x1080x24

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p uploads/media sessions/whatsapp

# Copy start script
COPY start_with_vnc.sh /app/start_with_vnc.sh
RUN chmod +x /app/start_with_vnc.sh

# Expose ports
ENV PORT=8080
EXPOSE 8080
EXPOSE 6080

# Run the application with VNC
CMD ["/app/start_with_vnc.sh"]
