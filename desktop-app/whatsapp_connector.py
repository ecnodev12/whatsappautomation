#!/usr/bin/env python3
"""
WhatsApp Connector - Desktop App
Runs on user's computer to control their local Chrome browser
"""

import asyncio
import json
import platform
import sys
import time
from playwright.sync_api import sync_playwright, Browser, Page
import websockets
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Configuration
WEBSOCKET_URL = "wss://your-app.onrender.com/ws/connector"  # Update with your domain
VERSION = "1.0.0"

class WhatsAppConnector:
    def __init__(self):
        self.playwright = None
        self.browser = None
        self.page = None
        self.is_connected = False
        self.is_logged_in = False
        self.websocket = None
        self.connector_id = None
        self.gui = None
        
    def start_gui(self):
        """Start the GUI"""
        self.gui = ConnectorGUI(self)
        self.gui.run()
    
    def start_browser(self):
        """Start Chrome browser with WhatsApp Web"""
        try:
            self.playwright = sync_playwright().start()
            
            # Launch browser in headed mode (visible to user)
            self.browser = self.playwright.chromium.launch(
                headless=False,
                channel="chrome",  # Use user's installed Chrome
                args=['--start-maximized']
            )
            
            # Create context
            context = self.browser.new_context(
                viewport={'width': 1920, 'height': 1080}
            )
            
            self.page = context.new_page()
            self.page.goto('https://web.whatsapp.com')
            self.is_connected = True
            
            if self.gui:
                self.gui.update_status("✅ Browser Connected", "green")
            
            # Check if logged in
            self.check_login()
            
            return True
            
        except Exception as e:
            print(f"Browser start error: {e}")
            if self.gui:
                self.gui.update_status(f"❌ Error: {e}", "red")
            return False
    
    def check_login(self):
        """Check if logged into WhatsApp"""
        try:
            # Wait for either QR code or chat list
            time.sleep(5)
            
            # Check if chat list is visible
            chat_list = self.page.query_selector('#side')
            if chat_list:
                self.is_logged_in = True
                if self.gui:
                    self.gui.update_status("✅ Logged into WhatsApp", "green")
                return True
            else:
                self.is_logged_in = False
                if self.gui:
                    self.gui.update_status("⚠️ Please scan QR code", "orange")
                return False
                
        except Exception as e:
            print(f"Login check error: {e}")
            return False
    
    def send_message(self, phone, message):
        """Send message to phone number"""
        try:
            if not self.is_logged_in:
                return {'success': False, 'error': 'Not logged in'}
            
            # Navigate to chat
            url = f'https://web.whatsapp.com/send?phone={phone}'
            self.page.goto(url, wait_until='domcontentloaded')
            time.sleep(3)
            
            # Type message
            message_box = self.page.wait_for_selector('div[contenteditable="true"][data-tab="10"]', timeout=10000)
            if message_box:
                message_box.click()
                message_box.type(message, delay=50)
                time.sleep(1)
                
                # Click send button
                send_button = self.page.query_selector('button[data-tab="11"]')
                if send_button:
                    send_button.click()
                    time.sleep(2)
                    return {'success': True}
            
            return {'success': False, 'error': 'Could not find message box'}
            
        except Exception as e:
            print(f"Send message error: {e}")
            return {'success': False, 'error': str(e)}
    
    async def connect_websocket(self):
        """Connect to website's WebSocket server"""
        try:
            async with websockets.connect(WEBSOCKET_URL) as websocket:
                self.websocket = websocket
                
                # Send registration
                await websocket.send(json.dumps({
                    'type': 'register',
                    'device': platform.system(),
                    'version': VERSION
                }))
                
                # Listen for commands
                async for message in websocket:
                    data = json.loads(message)
                    await self.handle_command(data)
                    
        except Exception as e:
            print(f"WebSocket error: {e}")
            if self.gui:
                self.gui.update_status(f"❌ Connection lost: {e}", "red")
    
    async def handle_command(self, data):
        """Handle command from website"""
        cmd_type = data.get('type')
        
        if cmd_type == 'send_message':
            result = self.send_message(data['phone'], data['message'])
            await self.websocket.send(json.dumps({
                'type': 'message_result',
                'result': result,
                'phone': data['phone']
            }))
        
        elif cmd_type == 'check_status':
            await self.websocket.send(json.dumps({
                'type': 'status',
                'connected': self.is_connected,
                'logged_in': self.is_logged_in
            }))
        
        elif cmd_type == 'ping':
            await self.websocket.send(json.dumps({'type': 'pong'}))
    
    def run_websocket_thread(self):
        """Run WebSocket in separate thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self.connect_websocket())
    
    def cleanup(self):
        """Cleanup resources"""
        if self.page:
            self.page.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()


class ConnectorGUI:
    def __init__(self, connector):
        self.connector = connector
        self.root = tk.Tk()
        self.root.title("WhatsApp Connector")
        self.root.geometry("400x300")
        self.root.resizable(False, False)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup GUI elements"""
        # Title
        title = tk.Label(
            self.root,
            text="📱 WhatsApp Connector",
            font=("Arial", 20, "bold"),
            fg="#25D366"
        )
        title.pack(pady=20)
        
        # Status
        self.status_label = tk.Label(
            self.root,
            text="⚪ Not Connected",
            font=("Arial", 12),
            fg="gray"
        )
        self.status_label.pack(pady=10)
        
        # Connect button
        self.connect_btn = ttk.Button(
            self.root,
            text="Connect to WhatsApp Web",
            command=self.on_connect
        )
        self.connect_btn.pack(pady=10)
        
        # Info
        info = tk.Label(
            self.root,
            text="Keep this window open while using\nthe website dashboard",
            font=("Arial", 9),
            fg="gray"
        )
        info.pack(pady=20)
        
        # Website button
        website_btn = ttk.Button(
            self.root,
            text="Open Website Dashboard",
            command=self.open_website
        )
        website_btn.pack(pady=5)
        
        # Version
        version_label = tk.Label(
            self.root,
            text=f"v{VERSION}",
            font=("Arial", 8),
            fg="lightgray"
        )
        version_label.pack(side="bottom", pady=5)
    
    def on_connect(self):
        """Handle connect button click"""
        self.update_status("🔄 Starting browser...", "blue")
        self.connect_btn.config(state="disabled")
        
        # Start browser in separate thread
        threading.Thread(target=self._connect_thread, daemon=True).start()
    
    def _connect_thread(self):
        """Connect in background thread"""
        success = self.connector.start_browser()
        
        if success:
            # Start WebSocket connection
            threading.Thread(target=self.connector.run_websocket_thread, daemon=True).start()
        else:
            self.connect_btn.config(state="normal")
    
    def update_status(self, text, color):
        """Update status label"""
        self.status_label.config(text=text, fg=color)
    
    def open_website(self):
        """Open website in default browser"""
        import webbrowser
        webbrowser.open("https://your-app.onrender.com")  # Update with your domain
    
    def run(self):
        """Run GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.mainloop()
    
    def on_close(self):
        """Handle window close"""
        if messagebox.askokcancel("Quit", "Close WhatsApp Connector?"):
            self.connector.cleanup()
            self.root.destroy()
            sys.exit(0)


def main():
    """Main entry point"""
    print("WhatsApp Connector v" + VERSION)
    print("Starting...")
    
    connector = WhatsAppConnector()
    connector.start_gui()


if __name__ == "__main__":
    main()
