# WhatsApp Connector - Desktop App

This desktop app runs on the user's computer and controls their local Chrome browser.

## 🚀 For Users

### Installation:

1. **Download** the app for your system:
   - Windows: `WhatsAppConnector.exe`
   - Mac: `WhatsAppConnector.app`
   - Linux: `WhatsAppConnector`

2. **Run** the app

3. **Click** "Connect to WhatsApp Web"
   - Your Chrome browser will open
   - Scan QR code if not logged in

4. **Open** the website dashboard in your browser

5. **Start** sending messages from the website!

### Usage:

- Keep the connector app running while using the website
- The app window shows connection status
- You can minimize it to system tray
- Click "Open Website Dashboard" to access the control panel

---

## 🔧 For Developers

### Setup Development Environment:

```bash
cd desktop-app

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium

# Run the app
python whatsapp_connector.py
```

### Build Executable:

```bash
# Build for current platform
python build.py

# Output will be in dist/ folder
```

### Configuration:

Update `WEBSOCKET_URL` in `whatsapp_connector.py`:

```python
WEBSOCKET_URL = "wss://your-domain.com/ws/connector"
```

---

## 🏗️ How It Works

```
Desktop App (User's Computer)
    ↓
Opens Chrome Browser (headed mode)
    ↓
Loads WhatsApp Web
    ↓
Connects to Website via WebSocket
    ↓
Receives commands from website
    ↓
Executes in local browser
    ↓
Sends results back to website
```

### Commands Supported:

- `send_message` - Send message to phone number
- `check_status` - Get connection status
- `ping` - Keep connection alive

### WebSocket Protocol:

**From App to Website:**
```json
{
  "type": "register",
  "device": "Windows",
  "version": "1.0.0"
}
```

**From Website to App:**
```json
{
  "type": "send_message",
  "phone": "1234567890",
  "message": "Hello!"
}
```

**From App to Website:**
```json
{
  "type": "message_result",
  "result": {"success": true},
  "phone": "1234567890"
}
```

---

## 📦 Distribution

### For Users:
- Host executables on GitHub Releases
- Or on your website's download page
- Include installation instructions

### File Sizes:
- Windows: ~50MB
- Mac: ~60MB  
- Linux: ~55MB

---

## 🔐 Security

- App only communicates with your website
- No data stored locally except WhatsApp session
- WebSocket connection is encrypted (WSS)
- User can see all activity in browser

---

## 🐛 Troubleshooting

### "Chrome not found"
- Install Google Chrome on your computer
- Or use `chromium` channel instead of `chrome`

### "Cannot connect to website"
- Check WEBSOCKET_URL is correct
- Ensure website is running
- Check firewall settings

### "Browser closes immediately"
- Check Playwright installation
- Try running: `playwright install chromium`

---

## 📝 License

Same as main project
