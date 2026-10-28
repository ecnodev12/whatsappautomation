// Background service worker

console.log('WhatsApp Bulk Sender Background Service started');

// Listen for extension installation
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

// Handle messages from content script or popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  // Handle any background tasks here if needed
  return true;
});
