// Popup script for WhatsApp Bulk Sender Extension

let contacts = [];
let currentIndex = 0;
let isPaused = false;
let isSending = false;

// DOM Elements
const statusDot = document.getElementById('statusDot');
const statusText = document.getElementById('statusText');
const connectBtn = document.getElementById('connectBtn');
const uploadSection = document.getElementById('uploadSection');
const campaignSection = document.getElementById('campaignSection');
const fileInput = document.getElementById('fileInput');
const messageTemplate = document.getElementById('messageTemplate');
const uploadBtn = document.getElementById('uploadBtn');
const startBtn = document.getElementById('startBtn');
const pauseBtn = document.getElementById('pauseBtn');
const stopBtn = document.getElementById('stopBtn');
const totalContacts = document.getElementById('totalContacts');
const sentCount = document.getElementById('sentCount');
const failedCount = document.getElementById('failedCount');
const progressFill = document.getElementById('progressFill');

// Check WhatsApp Web status
async function checkWhatsAppStatus() {
  try {
    const [tab] = await chrome.tabs.query({ url: 'https://web.whatsapp.com/*' });
    
    if (tab) {
      // Check if logged in
      const result = await chrome.tabs.sendMessage(tab.id, { action: 'checkLogin' });
      
      if (result && result.loggedIn) {
        statusDot.classList.add('connected');
        statusText.textContent = 'Connected to WhatsApp Web';
        connectBtn.textContent = 'View WhatsApp Web';
        uploadSection.style.display = 'block';
        return true;
      }
    }
    
    statusDot.classList.remove('connected');
    statusText.textContent = 'Not Connected';
    connectBtn.textContent = 'Open WhatsApp Web';
    uploadSection.style.display = 'none';
    campaignSection.style.display = 'none';
    return false;
  } catch (error) {
    console.error('Status check error:', error);
    return false;
  }
}

// Open WhatsApp Web
connectBtn.addEventListener('click', async () => {
  const [tab] = await chrome.tabs.query({ url: 'https://web.whatsapp.com/*' });
  
  if (tab) {
    chrome.tabs.update(tab.id, { active: true });
    chrome.windows.update(tab.windowId, { focused: true });
  } else {
    chrome.tabs.create({ url: 'https://web.whatsapp.com' });
  }
  
  setTimeout(checkWhatsAppStatus, 2000);
});

// File input handler
fileInput.addEventListener('change', () => {
  uploadBtn.disabled = !fileInput.files.length;
});

// Upload contacts
uploadBtn.addEventListener('click', async () => {
  const file = fileInput.files[0];
  if (!file) return;
  
  // Read file
  const reader = new FileReader();
  reader.onload = async (e) => {
    const data = new Uint8Array(e.target.result);
    
    // Parse Excel/CSV using SheetJS (we'll inject this library)
    try {
      // For now, show alert - need to add XLSX library
      alert('Excel parsing requires SheetJS library. For this demo, use CSV format.');
      
      // Parse CSV
      if (file.name.endsWith('.csv')) {
        const text = new TextDecoder().decode(data);
        parseCSV(text);
      }
    } catch (error) {
      alert('Error parsing file: ' + error.message);
    }
  };
  
  reader.readAsArrayBuffer(file);
});

// Parse CSV
function parseCSV(text) {
  const lines = text.split('\\n');
  const headers = lines[0].toLowerCase().split(',').map(h => h.trim());
  
  contacts = [];
  
  for (let i = 1; i < lines.length; i++) {
    if (!lines[i].trim()) continue;
    
    const values = lines[i].split(',');
    const contact = {};
    
    headers.forEach((header, index) => {
      contact[header] = values[index]?.trim() || '';
    });
    
    if (contact.phone) {
      // Apply message template
      let message = messageTemplate.value || contact.message || '';
      if (contact.name) {
        message = message.replace(/{{name}}/g, contact.name);
      }
      
      contacts.push({
        name: contact.name || '',
        phone: contact.phone.replace(/\\D/g, ''), // Remove non-digits
        message: message,
        status: 'pending'
      });
    }
  }
  
  if (contacts.length > 0) {
    totalContacts.textContent = contacts.length;
    sentCount.textContent = '0';
    failedCount.textContent = '0';
    campaignSection.style.display = 'block';
    alert(`${contacts.length} contacts loaded successfully!`);
    
    // Save to storage
    chrome.storage.local.set({ contacts, currentIndex: 0 });
  } else {
    alert('No valid contacts found in file!');
  }
}

// Start campaign
startBtn.addEventListener('click', async () => {
  if (contacts.length === 0) {
    alert('Please upload contacts first!');
    return;
  }
  
  const [tab] = await chrome.tabs.query({ url: 'https://web.whatsapp.com/*' });
  
  if (!tab) {
    alert('Please open WhatsApp Web first!');
    return;
  }
  
  isSending = true;
  isPaused = false;
  startBtn.style.display = 'none';
  pauseBtn.style.display = 'block';
  stopBtn.style.display = 'block';
  
  // Start sending
  sendNextMessage(tab.id);
});

// Pause campaign
pauseBtn.addEventListener('click', () => {
  isPaused = true;
  pauseBtn.textContent = '▶️ Resume';
  pauseBtn.onclick = () => {
    isPaused = false;
    pauseBtn.textContent = '⏸️ Pause';
    const [tab] = chrome.tabs.query({ url: 'https://web.whatsapp.com/*' }).then(([tab]) => {
      if (tab) sendNextMessage(tab.id);
    });
  };
});

// Stop campaign
stopBtn.addEventListener('click', () => {
  isSending = false;
  isPaused = false;
  currentIndex = 0;
  startBtn.style.display = 'block';
  pauseBtn.style.display = 'none';
  stopBtn.style.display = 'none';
  pauseBtn.textContent = '⏸️ Pause';
});

// Send next message
async function sendNextMessage(tabId) {
  if (!isSending || isPaused) return;
  
  if (currentIndex >= contacts.length) {
    // Campaign complete
    alert('Campaign completed!');
    stopBtn.click();
    return;
  }
  
  const contact = contacts[currentIndex];
  
  try {
    // Send message via content script
    const result = await chrome.tabs.sendMessage(tabId, {
      action: 'sendMessage',
      phone: contact.phone,
      message: contact.message
    });
    
    if (result && result.success) {
      contact.status = 'sent';
      sentCount.textContent = parseInt(sentCount.textContent) + 1;
    } else {
      contact.status = 'failed';
      failedCount.textContent = parseInt(failedCount.textContent) + 1;
    }
  } catch (error) {
    console.error('Send error:', error);
    contact.status = 'failed';
    failedCount.textContent = parseInt(failedCount.textContent) + 1;
  }
  
  currentIndex++;
  
  // Update progress
  const progress = (currentIndex / contacts.length) * 100;
  progressFill.style.width = progress + '%';
  
  // Save progress
  chrome.storage.local.set({ contacts, currentIndex });
  
  // Wait 5-10 seconds before next message
  const delay = 5000 + Math.random() * 5000;
  setTimeout(() => sendNextMessage(tabId), delay);
}

// Load saved data
chrome.storage.local.get(['contacts', 'currentIndex'], (data) => {
  if (data.contacts) {
    contacts = data.contacts;
    currentIndex = data.currentIndex || 0;
    
    if (contacts.length > 0) {
      totalContacts.textContent = contacts.length;
      const sent = contacts.filter(c => c.status === 'sent').length;
      const failed = contacts.filter(c => c.status === 'failed').length;
      sentCount.textContent = sent;
      failedCount.textContent = failed;
      campaignSection.style.display = 'block';
      
      const progress = (currentIndex / contacts.length) * 100;
      progressFill.style.width = progress + '%';
    }
  }
});

// Check status on load
checkWhatsAppStatus();

// Refresh status every 3 seconds
setInterval(checkWhatsAppStatus, 3000);
