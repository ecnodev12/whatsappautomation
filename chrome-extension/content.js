// Content script for WhatsApp Web interaction

console.log('WhatsApp Bulk Sender Extension loaded');

// Check if user is logged in
function checkLogin() {
  const chatList = document.querySelector('#side');
  const pane = document.querySelector('#pane-side');
  return !!(chatList || pane);
}

// Send message to a phone number
async function sendMessage(phone, message) {
  try {
    // Open chat with phone number
    const url = `https://web.whatsapp.com/send?phone=${phone}&text=${encodeURIComponent(message)}`;
    window.location.href = url;
    
    // Wait for page to load
    await new Promise(resolve => setTimeout(resolve, 3000));
    
    // Find and click send button
    const sendButton = document.querySelector('button[aria-label="Send"]') || 
                      document.querySelector('span[data-icon="send"]')?.parentElement;
    
    if (sendButton) {
      sendButton.click();
      await new Promise(resolve => setTimeout(resolve, 1000));
      return { success: true };
    } else {
      return { success: false, error: 'Send button not found' };
    }
  } catch (error) {
    console.error('Send message error:', error);
    return { success: false, error: error.message };
  }
}

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'checkLogin') {
    sendResponse({ loggedIn: checkLogin() });
  } else if (request.action === 'sendMessage') {
    sendMessage(request.phone, request.message).then(sendResponse);
    return true; // Keep channel open for async response
  }
});
