/* ═══════════════ WA Bulk Sender — App Logic ═══════════════ */

let currentCampaignId = null;
let currentAttachment = null;  // { file, type, previewUrl }
let statusPollInterval = null;
let campaignPollInterval = null;

/* ────────────── Init ────────────── */
document.addEventListener('DOMContentLoaded', () => {
  showView('dashboard', document.querySelector('.nav-item'));
  loadCampaigns();
  pollWhatsAppStatus();
  statusPollInterval = setInterval(pollWhatsAppStatus, 5000);
  document.addEventListener('click', (e) => {
    if (!e.target.closest('#attachTrigger') && !e.target.closest('#attachMenu'))
      document.getElementById('attachMenu').style.display = 'none';
  });
});

/* ────────────── View switching ────────────── */
function showView(name, el) {
  document.querySelectorAll('.view').forEach(v => v.style.display = 'none');
  const view = document.getElementById(`view-${name}`);
  if (view) view.style.display = 'block';

  document.querySelectorAll('.nav-item').forEach(i => i.classList.remove('active'));
  if (el) el.classList.add('active');

  const titles = { dashboard: 'Dashboard', 'new-campaign': 'New Campaign', campaigns: 'Campaigns', groups: 'Group Contacts Grabber' };
  document.getElementById('topbarTitle').textContent = titles[name] || name;

  if (name === 'campaigns') loadCampaigns();
  if (name === 'dashboard') updateDashboardSummary();
  if (name === 'groups') loadStudioGroups();
}

function toggleSidebar() {
  document.getElementById('sidebar').classList.toggle('open');
}

/* ────────────── Toast ────────────── */
function toast(msg, type = 'info') {
  const icons = { success: '✓', error: '✗', info: 'ℹ', warning: '⚠' };
  const tc = document.getElementById('toastContainer');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.innerHTML = `<span>${icons[type] || ''}</span><span>${msg}</span>`;
  tc.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}

/* ────────────── Inline messages ────────────── */
function showMsg(id, msg, type = 'info') {
  const el = document.getElementById(id);
  if (!el) return;
  el.textContent = msg;
  el.className = `inline-msg ${type}`;
  el.style.display = 'block';
  if (type !== 'error') setTimeout(() => el.style.display = 'none', 5000);
}

/* ────────────── WhatsApp status ────────────── */
async function pollWhatsAppStatus() {
  try {
    const r = await fetch('/api/whatsapp/status');
    const d = await r.json();
    if (!d.success) return;
    updateStatusUI(d.status);
  } catch (e) {}
}

function updateStatusUI(status) {
  const connected = status.is_connected;
  const loggedIn  = status.is_logged_in;
  const dotClass  = loggedIn ? 'connected' : (connected ? 'connecting' : 'disconnected');
  const label     = loggedIn ? 'Connected' : (connected ? 'Connecting…' : 'Disconnected');

  document.querySelectorAll('.wa-status-dot').forEach(d => {
    d.className = `wa-status-dot ${dotClass}`;
  });
  document.querySelectorAll('.status-dot').forEach(d => {
    d.className = `status-dot ${dotClass}`;
  });
  ['sidebarStatusText', 'topbarStatusText'].forEach(id => {
    const el = document.getElementById(id);
    if (el) el.textContent = label;
  });

  const connectMini = document.getElementById('connectMiniBtn');
  if (connectMini) connectMini.textContent = loggedIn ? 'Logout' : 'Connect';
  if (connectMini) connectMini.onclick = loggedIn ? logoutWhatsApp : connectWhatsApp;

  const connectCard = document.getElementById('connectCard');
  if (connectCard) connectCard.style.display = loggedIn ? 'none' : 'block';

  const logoutTopBtn = document.getElementById('logoutTopBtn');
  if (logoutTopBtn) logoutTopBtn.style.display = loggedIn ? 'inline-flex' : 'none';
}

async function connectWhatsApp() {
  const btn = document.getElementById('connectBtn');
  if (btn) { btn.textContent = 'Connecting…'; btn.disabled = true; }
  try {
    const r = await fetch('/api/whatsapp/connect', { method: 'POST' });
    const d = await r.json();
    if (d.success) {
      toast('Connected! Scan QR code to login', 'success');
      showMsg('connectionMessage', 'Browser connected. Scan QR code in the browser or check status.', 'success');
      // Show QR code in modal
      setTimeout(showQRCodeModal, 3000);
    } else {
      toast(d.error || 'Connection failed', 'error');
    }
  } catch (e) {
    toast('Connection error', 'error');
  } finally {
    if (btn) { btn.textContent = 'Connect Now'; btn.disabled = false; }
  }
}

let qrPollInterval = null;

async function showQRCodeModal() {
  // Create modal if it doesn't exist
  let modal = document.getElementById('qrModal');
  if (!modal) {
    modal = document.createElement('div');
    modal.id = 'qrModal';
    modal.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.8);display:flex;align-items:center;justify-content:center;z-index:10000;';
    modal.innerHTML = `
      <div style="background:white;padding:30px;border-radius:12px;text-align:center;max-width:400px;">
        <h2 style="margin:0 0 20px 0;color:#25D366;">Scan QR Code</h2>
        <div id="qrCodeContainer" style="min-height:300px;display:flex;align-items:center;justify-content:center;flex-direction:column;">
          <div style="color:#666;margin-bottom:10px;">⏳ Starting browser...</div>
          <div style="color:#999;font-size:14px;">Render free tier can take 30-60 seconds</div>
          <div style="color:#999;font-size:14px;margin-top:10px;">Please be patient...</div>
        </div>
        <p style="color:#666;margin:20px 0 0 0;">Scan this code with WhatsApp on your phone</p>
        <button onclick="closeQRModal()" style="margin-top:20px;padding:10px 20px;background:#dc3545;color:white;border:none;border-radius:6px;cursor:pointer;">Close</button>
      </div>
    `;
    document.body.appendChild(modal);
  }
  modal.style.display = 'flex';
  
  // Wait 15 seconds before first poll to let browser fully start on Render
  setTimeout(() => {
    pollQRCode();
    qrPollInterval = setInterval(pollQRCode, 4000); // Poll every 4 seconds
  }, 15000);
}

async function pollQRCode() {
  try {
    const r = await fetch('/api/whatsapp/qrcode');
    const d = await r.json();
    const container = document.getElementById('qrCodeContainer');
    
    if (d.success && d.qr_code) {
      container.innerHTML = `<img src="${d.qr_code}" style="width:280px;height:280px;border:2px solid #ddd;padding:10px;background:white;border-radius:8px;" alt="WhatsApp QR Code">`;
    } else if (d.error && d.error.includes('Already logged in')) {
      clearInterval(qrPollInterval);
      closeQRModal();
      toast('Already logged in to WhatsApp!', 'success');
    } else {
      // Show the actual error message from backend
      const errorMsg = d.error || 'Waiting for QR code...';
      container.innerHTML = `
        <div style="color:#666;text-align:center;padding:20px;">
          <div style="font-size:48px;margin-bottom:15px;">⏳</div>
          <div>${errorMsg}</div>
        </div>
      `;
    }
  } catch (e) {
    console.error('QR poll error:', e);
    const container = document.getElementById('qrCodeContainer');
    if (container) {
      container.innerHTML = `<div style="color:#dc3545;">Connection error. Please refresh and try again.</div>`;
    }
  }
}

function closeQRModal() {
  const modal = document.getElementById('qrModal');
  if (modal) modal.style.display = 'none';
  if (qrPollInterval) {
    clearInterval(qrPollInterval);
    qrPollInterval = null;
  }
}

async function logoutWhatsApp() {
  if (!confirm('Logout from WhatsApp Web?')) return;
  try {
    await fetch('/api/whatsapp/logout', { method: 'POST' });
    toast('Logged out', 'info');
    updateStatusUI({ is_connected: false, is_logged_in: false });
  } catch (e) {
    toast('Logout failed', 'error');
  }
}

/* ────────────── Attachment ────────────── */
function toggleAttachMenu(e) {
  e.stopPropagation();
  const m = document.getElementById('attachMenu');
  m.style.display = m.style.display === 'none' ? 'block' : 'none';
}

function triggerFileInput(type) {
  document.getElementById('attachMenu').style.display = 'none';
  document.getElementById(`mediaInput${type.charAt(0).toUpperCase() + type.slice(1)}`).click();
}

function handleFileSelected(input, type) {
  const file = input.files[0];
  if (!file) return;
  currentAttachment = { file, type };

  const strip = document.getElementById('attachPreview');
  const inner = document.getElementById('attachPreviewInner');
  const icons = { image: '🖼️', document: '📄', audio: '🎵' };

  let preview = `<span>${icons[type] || '📎'}</span><span><strong>${file.name}</strong> (${formatBytes(file.size)})</span>`;
  if (type === 'image' && file.type.startsWith('image/')) {
    const url = URL.createObjectURL(file);
    preview = `<img src="${url}" style="height:48px;border-radius:6px;object-fit:cover"> <span>${file.name}</span>`;
  }
  inner.innerHTML = preview;
  strip.style.display = 'flex';
  toast(`Attached: ${file.name}`, 'success');
  input.value = '';
}

function clearAttachment() {
  currentAttachment = null;
  document.getElementById('attachPreview').style.display = 'none';
  document.getElementById('attachPreviewInner').innerHTML = '';
}

function formatBytes(b) {
  if (b < 1024) return b + ' B';
  if (b < 1048576) return (b/1024).toFixed(1) + ' KB';
  return (b/1048576).toFixed(1) + ' MB';
}

function updateCharCount() {
  const ta = document.getElementById('campaignMessage');
  document.getElementById('charCount').textContent = `${ta.value.length} / 4096`;
}

function insertPlaceholder() {
  const ta = document.getElementById('campaignMessage');
  const s = ta.selectionStart, e = ta.selectionEnd;
  ta.value = ta.value.substring(0, s) + '{{name}}' + ta.value.substring(e);
  ta.selectionStart = ta.selectionEnd = s + 8;
  ta.focus();
  updateCharCount();
}

/* ────────────── Campaign create ────────────── */
async function createCampaign(e) {
  e.preventDefault();
  const name = document.getElementById('campaignName').value.trim();
  const message = document.getElementById('campaignMessage').value.trim();

  if (!name) return toast('Please enter a campaign name', 'warning');

  const btn = document.getElementById('createCampaignBtn');
  btn.textContent = 'Creating…'; btn.disabled = true;

  try {
    const r = await fetch('/api/campaign/create', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, message_template: message })
    });
    const d = await r.json();
    if (!d.success) { toast(d.error || 'Failed', 'error'); return; }

    currentCampaignId = d.campaign_id;
    toast(`Campaign "${name}" created!`, 'success');

    // Upload media if attached
    if (currentAttachment) {
      showMsg('createCampaignMessage', 'Uploading media to ImageKit…', 'info');
      const ok = await uploadCampaignMedia(currentCampaignId, currentAttachment);
      if (ok) toast('Media uploaded successfully', 'success');
      else toast('Media upload failed (campaign created without media)', 'warning');
      clearAttachment();
    }

    document.getElementById('createCampaignForm').reset();
    updateCharCount();

    // Show upload contacts section
    document.getElementById('uploadSection').style.display = 'block';
    document.getElementById('tipCard').style.display = 'none';
    document.getElementById('uploadCampaignBadge').textContent = name;

    showMsg('createCampaignMessage', `Campaign created! Now upload contacts below.`, 'success');
    updateCampaignDropdown();

  } catch (err) {
    toast('Error: ' + err.message, 'error');
  } finally {
    btn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg> Create Campaign';
    btn.disabled = false;
  }
}

async function uploadCampaignMedia(campaignId, attachment) {
  const fd = new FormData();
  fd.append('media', attachment.file, attachment.file.name);
  fd.append('media_type', attachment.type);
  const r = await fetch(`/api/campaign/${campaignId}/upload_media`, { method: 'POST', body: fd });
  const d = await r.json();
  return d.success;
}

/* ────────────── Drop zone ────────────── */
function onDragOver(e) { e.preventDefault(); document.getElementById('dropZone').classList.add('drag-over'); }
function onDragLeave(e) { document.getElementById('dropZone').classList.remove('drag-over'); }
function onDrop(e) {
  e.preventDefault();
  document.getElementById('dropZone').classList.remove('drag-over');
  const file = e.dataTransfer.files[0];
  if (file) { document.getElementById('fileInput').value = ''; setDropFile(file); }
}
function onFileInputChange(input) {
  if (input.files[0]) setDropFile(input.files[0]);
}
function setDropFile(file) {
  const allowed = ['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'application/vnd.ms-excel'];
  const name = file.name.toLowerCase();
  if (!name.endsWith('.csv') && !name.endsWith('.xlsx') && !name.endsWith('.xls')) {
    return toast('Only CSV and XLSX files are allowed', 'error');
  }
  const dt = new DataTransfer();
  dt.items.add(file);
  document.getElementById('fileInput').files = dt.files;
  document.getElementById('dropFileName').textContent = `📎 ${file.name}`;
}

/* ────────────── Upload contacts ────────────── */
async function uploadContacts(e) {
  e.preventDefault();
  const file = document.getElementById('fileInput').files[0];
  if (!file) return toast('Please select a file', 'warning');
  if (!currentCampaignId) return toast('No campaign selected', 'warning');

  const btn = document.getElementById('uploadBtn');
  btn.textContent = 'Uploading…'; btn.disabled = true;

  const fd = new FormData();
  fd.append('file', file);
  const msg = document.getElementById('messageTemplate').value.trim();
  if (msg) fd.append('message_template', msg);

  try {
    const r = await fetch(`/api/campaign/${currentCampaignId}/upload`, { method: 'POST', body: fd });
    const d = await r.json();

    if (!d.success) {
      showMsg('uploadMessage', d.error || 'Upload failed', 'error');
      toast(d.error || 'Upload failed', 'error');
      return;
    }

    let detail = `✓ Uploaded ${d.total} contacts.`;
    if (d.skipped) detail += ` Skipped: ${d.skipped}.`;
    if (d.errors && d.errors.length) detail += ` Warnings: ${d.errors.length}.`;

    showMsg('uploadMessage', detail, 'success');
    toast(`${d.total} contacts uploaded!`, 'success');
    document.getElementById('uploadForm').reset();
    document.getElementById('dropFileName').textContent = '';
    loadCampaigns();
    updateDashboardSummary();

  } catch (err) {
    showMsg('uploadMessage', err.message, 'error');
    toast(err.message, 'error');
  } finally {
    btn.innerHTML = '<svg width="16" height="16" fill="none" stroke="currentColor" stroke-width="2.5" viewBox="0 0 24 24"><polyline points="16 16 12 12 8 16"/><line x1="12" y1="12" x2="12" y2="21"/><path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3"/></svg> Upload Contacts';
    btn.disabled = false;
  }
}

/* ────────────── Load campaigns ────────────── */
async function loadCampaigns() {
  try {
    const r = await fetch('/api/campaigns');
    const d = await r.json();
    if (!d.success) return;
    renderCampaignsTable(d.campaigns);
    renderRecentCampaigns(d.campaigns.slice(0, 5));
    updateCampaignDropdown(d.campaigns);
    updateDashboardSummary(d.campaigns);
  } catch (e) {}
}

function renderCampaignsTable(campaigns) {
  const wrap = document.getElementById('campaignsList');
  if (!campaigns.length) {
    wrap.innerHTML = `<div class="empty-state">
      <svg width="40" height="40" fill="none" stroke="#ccc" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <p>No campaigns yet. <a href="#" onclick="showView('new-campaign', document.querySelector('.nav-item:nth-child(2)'))">Create your first campaign →</a></p>
    </div>`;
    return;
  }

  const rows = campaigns.map(c => `
    <tr onclick="openCampaign('${c.id}')">
      <td>
        <div class="campaign-name-cell">${esc(c.name)}</div>
        ${c.media_filename ? `<div class="campaign-media-tag">📎 ${esc(c.media_filename)}</div>` : ''}
      </td>
      <td>${formatDate(c.created_at)}</td>
      <td>${c.total || 0}</td>
      <td>${c.sent || 0}</td>
      <td>${c.failed || 0}</td>
      <td><span class="status-badge ${c.status || 'draft'}">${c.status || 'draft'}</span></td>
    </tr>
  `).join('');

  wrap.innerHTML = `<table class="campaigns-table">
    <thead><tr>
      <th>Campaign</th><th>Created</th><th>Total</th><th>Sent</th><th>Failed</th><th>Status</th>
    </tr></thead>
    <tbody>${rows}</tbody>
  </table>`;
}

function renderRecentCampaigns(campaigns) {
  const wrap = document.getElementById('recentCampaignsList');
  if (!campaigns.length) {
    wrap.innerHTML = `<div class="empty-state">
      <svg width="40" height="40" fill="none" stroke="#ccc" stroke-width="1.5" viewBox="0 0 24 24"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/></svg>
      <p>No campaigns yet. <a href="#" onclick="showView('new-campaign', document.querySelector('.nav-item:nth-child(2)'))">Create one →</a></p>
    </div>`;
    return;
  }
  const rows = campaigns.map(c => `
    <tr onclick="openCampaign('${c.id}')">
      <td><div class="campaign-name-cell">${esc(c.name)}</div></td>
      <td>${c.total || 0}</td>
      <td>${c.sent || 0}</td>
      <td><span class="status-badge ${c.status || 'draft'}">${c.status || 'draft'}</span></td>
    </tr>
  `).join('');
  wrap.innerHTML = `<table class="campaigns-table">
    <thead><tr><th>Campaign</th><th>Total</th><th>Sent</th><th>Status</th></tr></thead>
    <tbody>${rows}</tbody>
  </table>`;
}

function updateDashboardSummary(campaigns) {
  if (!campaigns) { fetch('/api/campaigns').then(r=>r.json()).then(d=>{ if(d.success) updateDashboardSummary(d.campaigns); }); return; }
  let total=0, sent=0, failed=0, pending=0;
  campaigns.forEach(c => { total+=c.total||0; sent+=c.sent||0; failed+=c.failed||0; pending+=c.pending||0; });
  document.getElementById('dashTotal').textContent   = total;
  document.getElementById('dashSent').textContent    = sent;
  document.getElementById('dashFailed').textContent  = failed;
  document.getElementById('dashPending').textContent = pending;
}

function updateCampaignDropdown(campaigns) {
  // No longer used in new UI but kept for compatibility
}

/* ────────────── Campaign modal ────────────── */
async function openCampaign(id) {
  currentCampaignId = id;
  document.getElementById('campaignModal').style.display = 'flex';

  const r = await fetch(`/api/campaign/${id}`);
  const d = await r.json();
  if (!d.success) return;

  const c = d.campaign;
  document.getElementById('modalCampaignName').textContent = c.name;

  const badge = document.getElementById('modalStatusBadge');
  badge.textContent = c.status || 'draft';
  badge.style.background = statusColor(c.status).bg;
  badge.style.color = statusColor(c.status).text;

  updateModalStats(c);

  // Media info
  const mi = document.getElementById('modalMediaInfo');
  if (c.media_filename) {
    document.getElementById('modalMediaFilename').textContent = c.media_filename;
    mi.style.display = 'flex';
  } else {
    mi.style.display = 'none';
  }

  updateModalButtons(c.status);
  filterContacts('all', document.querySelector('.ftab'));
  startCampaignPoll(id);
}

function updateModalStats(c) {
  document.getElementById('statTotal').textContent   = c.total   || 0;
  document.getElementById('statSent').textContent    = c.sent    || 0;
  document.getElementById('statFailed').textContent  = c.failed  || 0;
  document.getElementById('statPending').textContent = c.pending || 0;

  const pct = c.total > 0 ? Math.round(((c.sent + c.failed) / c.total) * 100) : 0;
  document.getElementById('progressBar').style.width = pct + '%';
  document.getElementById('progressText').textContent = pct + '%';
}

function updateModalButtons(status) {
  const show = (id, v) => { const el=document.getElementById(id); if(el) el.style.display=v?'inline-flex':'none'; };
  show('startBtn',  status === 'draft' || status === 'stopped' || status === 'completed');
  show('pauseBtn',  status === 'running');
  show('resumeBtn', status === 'paused');
  show('stopBtn',   status === 'running' || status === 'paused');
  show('restartBtn', status === 'completed' || status === 'stopped');
}

function statusColor(s) {
  const map = { running:{ bg:'#eff6ff', text:'#1d4ed8' }, completed:{ bg:'#f0fdf4', text:'#16a34a' },
    paused:{ bg:'#fffbeb', text:'#b45309' }, stopped:{ bg:'#fef2f2', text:'#dc2626' } };
  return map[s] || { bg:'#f3f4f6', text:'#6b7280' };
}

function closeCampaignModal(e) {
  if (e && e.target !== document.getElementById('campaignModal')) return;
  document.getElementById('campaignModal').style.display = 'none';
  if (campaignPollInterval) { clearInterval(campaignPollInterval); campaignPollInterval = null; }
  loadCampaigns();
}

function startCampaignPoll(id) {
  if (campaignPollInterval) clearInterval(campaignPollInterval);
  campaignPollInterval = setInterval(async () => {
    try {
      const r = await fetch(`/api/campaign/${id}/status`);
      const d = await r.json();
      if (!d.success) return;
      updateModalStats(d.stats);
      updateModalButtons(d.stats.status);
      const badge = document.getElementById('modalStatusBadge');
      if (badge) { badge.textContent = d.stats.status; const sc=statusColor(d.stats.status); badge.style.background=sc.bg; badge.style.color=sc.text; }
    } catch (e) {}
  }, 2000);
}

/* ────────────── Contacts list ────────────── */
async function filterContacts(status, btn) {
  if (btn) {
    document.querySelectorAll('.ftab').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  const url = `/api/campaign/${currentCampaignId}/contacts` + (status && status !== 'all' ? `?status=${status}` : '');
  const r = await fetch(url);
  const d = await r.json();
  if (!d.success) return;

  const list = document.getElementById('contactsList');
  if (!d.contacts.length) {
    list.innerHTML = `<div class="empty-state" style="padding:20px"><p>No contacts with status "${status}"</p></div>`;
    return;
  }
  list.innerHTML = d.contacts.map(c => {
    const initials = (c.name || c.phone).substring(0, 2).toUpperCase();
    const statusMap = { sent:'✓ Sent', failed:'✗ Failed', pending:'● Pending', sending:'↑ Sending' };
    return `<div class="contact-row">
      <div class="contact-avatar">${initials}</div>
      <div class="contact-info">
        <div class="contact-name">${esc(c.name || '—')}</div>
        <div class="contact-phone">📱 ${esc(c.phone)}</div>
        ${c.error ? `<div style="font-size:11px;color:#ef4444">${esc(c.error)}</div>` : ''}
      </div>
      <div class="contact-status ${c.status}">${statusMap[c.status] || c.status}</div>
    </div>`;
  }).join('');
}

/* ────────────── Campaign actions ────────────── */
async function startCampaign() {
  const r = await fetch(`/api/campaign/${currentCampaignId}/start`, { method: 'POST' });
  const d = await r.json();
  if (d.success) { toast('Campaign started!', 'success'); updateModalButtons('running'); }
  else toast(d.error || 'Failed to start', 'error');
}

async function pauseCampaign() {
  await fetch(`/api/campaign/${currentCampaignId}/pause`, { method: 'POST' });
  updateModalButtons('paused'); toast('Campaign paused', 'info');
}

async function resumeCampaign() {
  await fetch(`/api/campaign/${currentCampaignId}/resume`, { method: 'POST' });
  updateModalButtons('running'); toast('Campaign resumed', 'success');
}

async function stopCampaign() {
  if (!confirm('Stop this campaign?')) return;
  await fetch(`/api/campaign/${currentCampaignId}/stop`, { method: 'POST' });
  updateModalButtons('stopped'); toast('Campaign stopped', 'info');
}

async function restartCampaign() {
  if (!confirm('Restart this campaign? All contacts will be reset to pending status.')) return;
  const r = await fetch(`/api/campaign/${currentCampaignId}/restart`, { method: 'POST' });
  const d = await r.json();
  if (d.success) {
    toast(d.message || 'Campaign restarted successfully', 'success');
    loadCampaignDetails(currentCampaignId);
    updateModalButtons('draft');
  } else {
    toast(d.error || 'Failed to restart campaign', 'error');
  }
}

/* ────────────── Utils ────────────── */
function esc(s) {
  if (!s) return '';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

function formatDate(ts) {
  if (!ts) return '—';
  const d = ts._seconds ? new Date(ts._seconds * 1000) : new Date(ts);
  return d.toLocaleDateString('en-IN', { day:'2-digit', month:'short', year:'numeric' });
}

/* ═══════════════ WhatsApp Group Contacts Grabber ═══════════════ */

let cachedWhatsAppGroups = null;
let currentPreviewGroupJid = null;

// Tab switcher in New Campaign wizard
function switchContactTab(tab) {
  document.getElementById('tabBtnFile').classList.toggle('active', tab === 'file');
  document.getElementById('tabBtnGroups').classList.toggle('active', tab === 'groups');
  document.getElementById('contactTabFile').style.display = tab === 'file' ? 'block' : 'none';
  document.getElementById('contactTabGroups').style.display = tab === 'groups' ? 'block' : 'none';

  if (tab === 'groups') {
    loadWhatsAppGroupsForCampaign();
  }
}

// Fetch WhatsApp groups (common helper)
async function fetchWhatsAppGroups(force = false) {
  if (cachedWhatsAppGroups && !force) return cachedWhatsAppGroups;
  const res = await fetch('/api/whatsapp/groups');
  const data = await res.json();
  if (data.success && Array.isArray(data.groups)) {
    cachedWhatsAppGroups = data.groups;
    return cachedWhatsAppGroups;
  }
  throw new Error(data.error || 'Failed to fetch WhatsApp groups');
}

// ── Campaign Wizard Group Loader ──
async function loadWhatsAppGroupsForCampaign(force = false) {
  const listEl = document.getElementById('campaignGroupsList');
  const loadingEl = document.getElementById('campaignGroupsLoading');
  loadingEl.style.display = 'block';
  listEl.innerHTML = '';

  try {
    const groups = await fetchWhatsAppGroups(force);
    loadingEl.style.display = 'none';

    if (groups.length === 0) {
      listEl.innerHTML = '<div style="text-align:center; padding:20px; color:var(--text-3); font-size:13px;">No WhatsApp groups found. Make sure WhatsApp is connected.</div>';
      return;
    }

    renderCampaignGroups(groups);
  } catch (err) {
    loadingEl.style.display = 'none';
    listEl.innerHTML = `<div style="text-align:center; padding:16px; color:var(--danger); font-size:12px;">${esc(err.message)}</div>`;
  }
}

function renderCampaignGroups(groups) {
  const listEl = document.getElementById('campaignGroupsList');
  listEl.innerHTML = groups.map(g => `
    <label class="group-item" data-id="${esc(g.id)}" data-name="${esc(g.name.toLowerCase())}">
      <input type="checkbox" class="campaign-group-cb" value="${esc(g.id)}" onchange="updateCampaignSelectedGroupsCount()">
      <div class="group-avatar">👥</div>
      <div class="group-info">
        <div class="group-name">${esc(g.name)}</div>
        <div class="group-meta">${g.participants_count ? `${g.participants_count} members` : 'Group'}</div>
      </div>
      <span class="group-count-badge">${g.participants_count || 0}</span>
    </label>
  `).join('');
  updateCampaignSelectedGroupsCount();
}

function filterCampaignGroups() {
  const q = (document.getElementById('campaignGroupSearch').value || '').toLowerCase().trim();
  document.querySelectorAll('#campaignGroupsList .group-item').forEach(el => {
    const name = el.getAttribute('data-name') || '';
    el.style.display = (!q || name.includes(q)) ? 'flex' : 'none';
  });
}

function updateCampaignSelectedGroupsCount() {
  const checked = document.querySelectorAll('.campaign-group-cb:checked').length;
  document.getElementById('selectedGroupsCount').textContent = `${checked} group${checked === 1 ? '' : 's'} selected`;
}

// Import groups into current campaign (Wizard)
async function importGroupsToCampaign() {
  if (!currentCampaignId) return toast('Please create a campaign first', 'warning');
  const cbs = Array.from(document.querySelectorAll('.campaign-group-cb:checked'));
  const groupJids = cbs.map(cb => cb.value);

  if (groupJids.length === 0) {
    return toast('Please select at least one WhatsApp group', 'warning');
  }

  const btn = document.getElementById('campaignImportGroupsBtn');
  btn.textContent = 'Importing contacts…';
  btn.disabled = true;

  const excludeAdmins = document.getElementById('campaignExcludeAdmins').checked;

  try {
    const res = await fetch(`/api/campaign/${currentCampaignId}/import_group_contacts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_jids: groupJids, exclude_admins: excludeAdmins })
    });
    const d = await res.json();
    if (!d.success) {
      showMsg('campaignGroupImportMessage', d.error || 'Import failed', 'error');
      toast(d.error || 'Import failed', 'error');
      return;
    }

    showMsg('campaignGroupImportMessage', `✓ Successfully imported ${d.total} group contacts!`, 'success');
    toast(`Imported ${d.total} contacts!`, 'success');
    loadCampaigns();
    updateDashboardSummary();
  } catch (err) {
    showMsg('campaignGroupImportMessage', err.message, 'error');
    toast(err.message, 'error');
  } finally {
    btn.innerHTML = '👥 Import Selected Contacts';
    btn.disabled = false;
  }
}

// Export wizard selected groups to CSV
async function exportSelectedCampaignGroupsCSV() {
  const cbs = Array.from(document.querySelectorAll('.campaign-group-cb:checked'));
  const groupJids = cbs.map(cb => cb.value);
  if (groupJids.length === 0) return toast('Select at least one group to export', 'warning');
  downloadGroupsCSV(groupJids);
}

// ── Dedicated Studio View ──
async function loadStudioGroups(force = false) {
  const listEl = document.getElementById('studioGroupsList');
  const loadingEl = document.getElementById('studioGroupsLoading');
  loadingEl.style.display = 'block';
  listEl.innerHTML = '';

  // Also populate campaign select dropdown
  populateStudioCampaignSelect();

  try {
    const groups = await fetchWhatsAppGroups(force);
    loadingEl.style.display = 'none';

    document.getElementById('studioGroupsCountBadge').textContent = `${groups.length} Groups`;

    if (groups.length === 0) {
      listEl.innerHTML = '<div style="text-align:center; padding:30px; color:var(--text-3); font-size:13px;">No WhatsApp groups found. Ensure WhatsApp Web is connected.</div>';
      return;
    }

    renderStudioGroups(groups);
  } catch (err) {
    loadingEl.style.display = 'none';
    listEl.innerHTML = `<div style="text-align:center; padding:20px; color:var(--danger); font-size:13px;">${esc(err.message)}</div>`;
  }
}

function renderStudioGroups(groups) {
  const listEl = document.getElementById('studioGroupsList');
  listEl.innerHTML = groups.map(g => `
    <div class="group-item ${currentPreviewGroupJid === g.id ? 'active' : ''}" data-id="${esc(g.id)}" data-name="${esc(g.name.toLowerCase())}" onclick="handleStudioGroupClick(event, '${esc(g.id)}')">
      <input type="checkbox" class="studio-group-cb" value="${esc(g.id)}" onclick="event.stopPropagation(); updateStudioSelectedCount();">
      <div class="group-avatar">👥</div>
      <div class="group-info">
        <div class="group-name">${esc(g.name)}</div>
        <div class="group-meta">${g.participants_count ? `${g.participants_count} members` : 'Group'}</div>
      </div>
      <span class="group-count-badge">${g.participants_count || 0}</span>
    </div>
  `).join('');
  updateStudioSelectedCount();
}

function filterStudioGroups() {
  const q = (document.getElementById('studioGroupSearch').value || '').toLowerCase().trim();
  document.querySelectorAll('#studioGroupsList .group-item').forEach(el => {
    const name = el.getAttribute('data-name') || '';
    el.style.display = (!q || name.includes(q)) ? 'flex' : 'none';
  });
}

function selectAllStudioGroups(select) {
  document.querySelectorAll('.studio-group-cb').forEach(cb => {
    if (cb.closest('.group-item').style.display !== 'none') {
      cb.checked = select;
    }
  });
  updateStudioSelectedCount();
}

function updateStudioSelectedCount() {
  const checked = document.querySelectorAll('.studio-group-cb:checked').length;
  document.getElementById('studioSelectedGroupsLabel').textContent = `${checked} selected`;
}

async function handleStudioGroupClick(e, jid) {
  currentPreviewGroupJid = jid;
  document.querySelectorAll('#studioGroupsList .group-item').forEach(el => {
    el.classList.toggle('active', el.getAttribute('data-id') === jid);
  });
  previewGroupParticipants(jid);
}

async function previewGroupParticipants(jid) {
  const bodyEl = document.getElementById('studioParticipantsBody');
  const statusEl = document.getElementById('studioPreviewStatusText');
  statusEl.textContent = 'Loading members…';
  bodyEl.innerHTML = '<tr><td colspan="3" style="text-align:center; padding:30px;"><div class="spinner"></div></td></tr>';

  try {
    const res = await fetch(`/api/whatsapp/group/${encodeURIComponent(jid)}/participants`);
    const data = await res.json();
    if (!data.success) throw new Error(data.error || 'Failed to fetch members');

    const participants = data.participants || [];
    document.getElementById('studioParticipantsCountBadge').textContent = `${participants.length} Members`;
    statusEl.textContent = `${participants.length} members loaded`;

    if (participants.length === 0) {
      bodyEl.innerHTML = '<tr><td colspan="3" style="text-align:center; color:var(--text-3); padding:30px;">No members found in this group.</td></tr>';
      return;
    }

    bodyEl.innerHTML = participants.map(p => `
      <tr style="border-bottom:1px solid var(--border);">
        <td style="padding:8px 12px; font-weight:500;">📱 ${esc(p.phone)}</td>
        <td style="padding:8px 12px; color:var(--text);">${esc(p.name || '—')}</td>
        <td style="padding:8px 12px;">
          ${p.isAdmin ? '<span class="badge-admin">Admin</span>' : '<span class="badge-member">Member</span>'}
        </td>
      </tr>
    `).join('');
  } catch (err) {
    statusEl.textContent = 'Error loading members';
    bodyEl.innerHTML = `<tr><td colspan="3" style="text-align:center; color:var(--danger); padding:20px;">${esc(err.message)}</td></tr>`;
  }
}

async function populateStudioCampaignSelect() {
  try {
    const res = await fetch('/api/campaigns');
    const data = await res.json();
    if (data.success) {
      const sel = document.getElementById('studioTargetCampaignSelect');
      const cur = sel.value;
      sel.innerHTML = '<option value="">— Select Target Campaign —</option>' +
        data.campaigns.map(c => `<option value="${esc(c.id)}">${esc(c.name)} (${c.total || 0} contacts)</option>`).join('');
      if (cur) sel.value = cur;
    }
  } catch (_) {}
}

async function importStudioSelectedToCampaign() {
  const sel = document.getElementById('studioTargetCampaignSelect');
  const campaignId = sel.value;
  if (!campaignId) return toast('Please select a target campaign', 'warning');

  const cbs = Array.from(document.querySelectorAll('.studio-group-cb:checked'));
  let groupJids = cbs.map(cb => cb.value);

  if (groupJids.length === 0 && currentPreviewGroupJid) {
    groupJids = [currentPreviewGroupJid];
  }

  if (groupJids.length === 0) {
    return toast('Please select at least one group from the list', 'warning');
  }

  const btn = document.getElementById('studioImportBtn');
  btn.textContent = 'Importing…';
  btn.disabled = true;

  const excludeAdmins = document.getElementById('studioExcludeAdmins').checked;

  try {
    const res = await fetch(`/api/campaign/${campaignId}/import_group_contacts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_jids: groupJids, exclude_admins: excludeAdmins })
    });
    const d = await res.json();
    if (!d.success) {
      showMsg('studioImportMsg', d.error || 'Import failed', 'error');
      toast(d.error || 'Import failed', 'error');
      return;
    }

    showMsg('studioImportMsg', `✓ Imported ${d.total} contacts into campaign!`, 'success');
    toast(`Successfully imported ${d.total} contacts!`, 'success');
    loadCampaigns();
    populateStudioCampaignSelect();
  } catch (err) {
    showMsg('studioImportMsg', err.message, 'error');
    toast(err.message, 'error');
  } finally {
    btn.innerHTML = '+ Add to Campaign';
    btn.disabled = false;
  }
}

async function exportStudioSelectedCSV() {
  const cbs = Array.from(document.querySelectorAll('.studio-group-cb:checked'));
  let groupJids = cbs.map(cb => cb.value);
  if (groupJids.length === 0 && currentPreviewGroupJid) {
    groupJids = [currentPreviewGroupJid];
  }
  if (groupJids.length === 0) return toast('Select at least one group to export', 'warning');
  downloadGroupsCSV(groupJids);
}

async function downloadGroupsCSV(groupJids) {
  try {
    toast('Generating CSV download…', 'info');
    const res = await fetch('/api/whatsapp/groups/export_csv', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ group_jids: groupJids })
    });
    if (!res.ok) throw new Error('Export request failed');
    const blob = await res.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `whatsapp_groups_contacts_${Date.now()}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
    toast('CSV downloaded successfully!', 'success');
  } catch (err) {
    toast(`Export error: ${err.message}`, 'error');
  }
}
