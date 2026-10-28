# WhatsApp Bulk Message Sender - Chrome Extension

A Chrome extension to send bulk WhatsApp messages directly from your browser!

## ✅ How It Works

This extension runs **locally on your computer**, accessing your Chrome browser where you're logged into WhatsApp Web. No cloud servers needed!

## 📦 Installation

### 1. Create Icons (Temporary placeholders)

Create a folder `icons` inside `chrome-extension` and add three PNG files:
- `icon16.png` (16x16px)
- `icon48.png` (48x48px)  
- `icon128.png` (128x128px)

Or download free WhatsApp icons from flaticon.com

### 2. Load Extension in Chrome

1. Open Chrome and go to: `chrome://extensions/`
2. Enable "Developer mode" (toggle in top right)
3. Click "Load unpacked"
4. Select the `chrome-extension` folder
5. Extension installed! ✅

## 🚀 How to Use

### Step 1: Open WhatsApp Web
1. Click the extension icon in Chrome toolbar
2. Click "Open WhatsApp Web"
3. Scan QR code with your phone (if not logged in)
4. Wait for "Connected to WhatsApp Web" status

### Step 2: Prepare Your Contacts File

Create a CSV file with these columns:

```csv
name,phone,message
John Doe,1234567890,Hi John! This is a test message
Jane Smith,9876543210,Hello Jane! How are you?
```

**Or use a message template:**

```csv
name,phone
John Doe,1234567890
Jane Smith,9876543210
```

Then add template in extension: `Hi {{name}}, this is a test!`

### Step 3: Upload and Send

1. Click "Choose File" and select your CSV
2. (Optional) Add message template with `{{name}}` placeholder
3. Click "Upload Contacts"
4. Review stats (Total, Sent, Failed)
5. Click "▶️ Start Campaign"
6. Watch progress in real-time!

## ⚙️ Features

- ✅ **Runs locally** - No cloud servers, works on YOUR computer
- ✅ **Excel/CSV import** - Upload contact lists easily
- ✅ **Message templates** - Use {{name}} for personalization
- ✅ **Real-time progress** - See sent/failed counts
- ✅ **Pause/Resume** - Control campaign flow
- ✅ **Automatic delays** - 5-10 seconds between messages
- ✅ **Session persistence** - Resume from where you stopped

## 🔒 Privacy

- All data stays on YOUR computer
- No data sent to any server
- Extension only accesses WhatsApp Web
- No tracking or analytics

## ⚠️ Important Notes

1. **Use responsibly** - Only send to people who expect your messages
2. **WhatsApp limits** - Don't send too many messages too fast
3. **Keep tab open** - Don't close WhatsApp Web tab while sending
4. **Stay logged in** - Don't logout from WhatsApp Web

## 🐛 Troubleshooting

### "Not Connected" status
- Make sure WhatsApp Web is open in a tab
- Scan QR code if not logged in
- Refresh the tab

### Messages not sending
- Check if you're still logged into WhatsApp Web
- Make sure phone numbers are correct (include country code)
- Try pausing and resuming

### Extension not appearing
- Make sure you enabled Developer Mode
- Try reloading the extension
- Check Chrome console for errors

## 📝 CSV Format Examples

### Basic Format:
```csv
name,phone,message
Alice,919876543210,Hello Alice!
Bob,1234567890,Hi Bob!
```

### With Template:
```csv
name,phone
Alice,919876543210
Bob,1234567890
```
Template: `Hi {{name}}, special offer just for you!`

## 🎯 Comparison

| Feature | This Extension | Cloud Version |
|---------|---------------|---------------|
| Runs on | YOUR computer | Remote server |
| Browser | YOUR Chrome | Headless browser |
| Setup | Load extension | Deploy to cloud |
| Cost | FREE | Server costs |
| Speed | Fast | Depends on server |

## 💡 How It Actually Works

1. **Extension loads** when you open Chrome
2. **Content script** injects into WhatsApp Web tab
3. **Popup UI** lets you control everything
4. **Message sending** happens in YOUR browser
5. **Data stored** in Chrome local storage

This is EXACTLY how the "Whatsapp Bulk Message Sender" extension you mentioned works!

## 🔄 Differences from Cloud Version

| Aspect | Chrome Extension | Cloud (Render/Railway) |
|--------|------------------|----------------------|
| Where code runs | Your computer | Data center |
| Browser | Your Chrome | Virtual browser |
| Internet needed | Only for WhatsApp | For everything |
| Setup | Load in Chrome | Deploy code |
| QR scan | In browser tab | Via modal/VNC |

---

**This is the LOCAL solution you wanted!** 🎉

No cloud servers, no headless browsers, just YOUR Chrome browser doing the work!
