from playwright.sync_api import sync_playwright
import base64
import time
import random
import logging
import os
import queue
import requests
import tempfile
import threading
import mimetypes

from config import Config
from firebase_service import FirebaseService

logger = logging.getLogger(__name__)

IMAGE_EXTS = {'jpg', 'jpeg', 'png', 'gif', 'webp', 'bmp'}
VIDEO_EXTS = {'mp4', 'mov', 'avi', '3gp'}
DOC_EXTS   = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'txt', 'zip', 'rar', '7z', 'csv'}
AUDIO_EXTS = {'mp3', 'ogg', 'wav', 'm4a', 'aac', 'flac'}

# MIME map for common extensions
MIME_MAP = {
    'jpg': 'image/jpeg', 'jpeg': 'image/jpeg', 'png': 'image/png',
    'gif': 'image/gif', 'webp': 'image/webp', 'bmp': 'image/bmp',
    'mp4': 'video/mp4', 'mov': 'video/quicktime', 'avi': 'video/x-msvideo',
    '3gp': 'video/3gpp', 'mp3': 'audio/mpeg', 'ogg': 'audio/ogg',
    'wav': 'audio/wav', 'm4a': 'audio/mp4', 'aac': 'audio/aac',
    'flac': 'audio/flac', 'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'txt': 'text/plain', 'csv': 'text/csv',
    'zip': 'application/zip', 'rar': 'application/x-rar-compressed',
    '7z': 'application/x-7z-compressed',
}


class WhatsAppWorker:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.playwright = None
            self.browser = None
            self.context = None
            self.page = None
            self.is_connected = False
            self.is_logged_in = False
            self.current_campaign_id = None
            self.is_running = False
            self.is_paused = False
            self.worker_thread = None
            self.firebase = FirebaseService()
            self.message_queue = queue.Queue()
            self.result_queue = queue.Queue()
            self.browser_thread = None
            self.browser_thread_running = False
            self._initialized = True

    # ──────────────────────────────────────────────────────────────────────────
    # Browser lifecycle
    # ──────────────────────────────────────────────────────────────────────────

    def start_browser(self):
        if self.browser_thread and self.browser_thread.is_alive():
            time.sleep(2)
            return {'success': True, 'message': 'Browser already connected', 'is_logged_in': self.is_logged_in}

        self.browser_thread_running = True
        self.browser_thread = threading.Thread(target=self._browser_thread_worker, daemon=True)
        self.browser_thread.start()
        time.sleep(5)
        return {'success': True, 'message': 'Browser started. Please scan QR code if not logged in.', 'is_logged_in': self.is_logged_in}

    def _browser_thread_worker(self):
        try:
            self.playwright = sync_playwright().start()
            # Always run headless in cloud deployment
            headless_mode = True
            
            logger.info("Starting browser in headless mode for cloud deployment")
            
            self.context = self.playwright.chromium.launch_persistent_context(
                user_data_dir=Config.SESSION_FOLDER,
                headless=headless_mode,
                args=['--no-sandbox', '--disable-setuid-sandbox',
                      '--disable-dev-shm-usage', '--disable-blink-features=AutomationControlled']
            )
            for p in self.context.pages:
                try: p.close()
                except: pass

            self.page = self.context.new_page()
            self.browser = self.context.browser
            self.is_connected = True

            self.page.goto('https://web.whatsapp.com', wait_until='domcontentloaded', timeout=60000)
            logger.info("WhatsApp Web page loaded")
            time.sleep(8)  # Wait for QR code to render

            # ── Inject WA-JS once on page load ──────────────────────────────
            self._inject_wajs()

            self.check_login_status()

            while self.browser_thread_running:
                try:
                    msg_data = self.message_queue.get(timeout=1)
                except queue.Empty:
                    continue
                try:
                    if msg_data.get('action') == 'debug':
                        res = msg_data['fn'](self.page)
                        self.result_queue.put({'success': True, 'data': res})
                    elif msg_data.get('action') == 'get_groups':
                        res = self._fetch_groups_internal()
                        self.result_queue.put(res)
                    elif msg_data.get('action') == 'get_group_participants':
                        res = self._fetch_group_participants_internal(msg_data.get('group_jid'))
                        self.result_queue.put(res)
                    else:
                        result = self._send_message_internal(
                            msg_data['phone'],
                            msg_data['message'],
                            msg_data.get('media_url'),
                            msg_data.get('media_filename')
                        )
                        self.result_queue.put(result)
                except Exception as e:
                    logger.error(f"Browser thread loop error: {e}")
                    self.result_queue.put({'success': False, 'error': str(e)})

        except Exception as e:
            logger.error(f"Browser thread fatal: {e}")
            self.is_connected = False
            self.is_logged_in = False
        finally:
            self._cleanup_browser()

    # ──────────────────────────────────────────────────────────────────────────
    # WA-JS Injection
    # ──────────────────────────────────────────────────────────────────────────

    def _inject_wajs(self):
        """Inject the WPPConnect WA-JS library into the current page."""
        try:
            already = self.page.evaluate("() => typeof window.WPP !== 'undefined'")
            if already:
                logger.info("WA-JS already injected")
                return True
            wajs_path = os.path.join(os.path.dirname(__file__), 'static', 'wppconnect-wa.js')
            with open(wajs_path, 'r', encoding='utf-8') as f:
                js_code = f.read()
            self.page.evaluate(js_code)
            time.sleep(2)
            # Wait for WPP to be ready
            for _ in range(20):
                ready = self.page.evaluate("() => typeof window.WPP !== 'undefined'")
                if ready:
                    logger.info("✓ WA-JS injected successfully")
                    return True
                time.sleep(0.5)
            logger.warning("WA-JS injection timed out")
            return False
        except Exception as e:
            logger.error(f"_inject_wajs error: {e}")
            return False

    # ──────────────────────────────────────────────────────────────────────────
    # Core send logic  (WA-JS / WPP.chat API — no DOM hacking)
    # ──────────────────────────────────────────────────────────────────────────

    def _send_message_internal(self, phone, message, media_url=None, media_filename=None):
        """
        Send a WhatsApp message using WA-JS (WPP.chat API).

        Strategy (same as WASender / WPPConnect):
        1. Ensure WA-JS is injected into the page.
        2. Resolve media: use local file or download remote URL.
        3. Base64-encode the file bytes and build a data URI.
        4. Call WPP.chat.sendFileMessage(jid, dataUri, options) for media, or
           WPP.chat.sendTextMessage(jid, text) for text-only.
        This bypasses ALL file-input / DOM restrictions — works for every format.
        """
        tmp_media_path = None
        is_temp_file = False
        try:
            if not self.is_logged_in:
                raise Exception("Not logged into WhatsApp Web")
            if not self.page:
                raise Exception("Browser page not available")

            clean_message = str(message or '').replace('\u200b', '').strip()

            # ── 1. Ensure WA-JS is injected ───────────────────────────────────
            wpp_exists = self.page.evaluate("() => typeof window.WPP !== 'undefined'")
            if not wpp_exists:
                logger.info("WA-JS not present, injecting now…")
                self._inject_wajs()

            # ── 2. Resolve media file if present ──────────────────────────────
            ext = 'bin'
            if media_url:
                try:
                    if os.path.exists(media_url):
                        tmp_media_path = os.path.abspath(media_url)
                        is_temp_file = False
                        ext = tmp_media_path.rsplit('.', 1)[-1].lower() if '.' in tmp_media_path else 'bin'
                        logger.info(f"Using local media: {tmp_media_path} ({ext})")
                    else:
                        ext = media_url.split('?')[0].rsplit('.', 1)[-1].lower() if '.' in media_url else 'bin'
                        logger.info(f"Downloading media from URL ({ext}) …")
                        resp = requests.get(media_url, timeout=30)
                        resp.raise_for_status()
                        with tempfile.NamedTemporaryFile(
                                delete=False, suffix=f'.{ext}', dir=tempfile.gettempdir()) as tmp:
                            tmp.write(resp.content)
                            tmp_media_path = tmp.name
                            is_temp_file = True
                        logger.info(f"Downloaded to {tmp_media_path}")
                except Exception as dl_err:
                    logger.error(f"Failed to prepare media: {dl_err}")
                    tmp_media_path = None
                    if not clean_message:
                        return {'success': False, 'error': f'Failed to download media: {dl_err}'}

            # ── 3. Format JID ─────────────────────────────────────────────────
            # Strip any non-digit chars except leading +, then strip +
            digits_only = ''.join(c for c in str(phone) if c.isdigit())
            jid = f"{digits_only}@c.us"

            # ── 4. Send via WA-JS ─────────────────────────────────────────────
            if tmp_media_path and os.path.exists(tmp_media_path):
                result = self._send_media_wajs(jid, tmp_media_path, ext, clean_message, media_filename)
                if result.get('success'):
                    return result
                # Fall through to text fallback if media failed and we have text
                logger.warning(f"WA-JS media send failed: {result.get('error')}")
                if not clean_message:
                    return result
                logger.info("Falling back to text-only send…")

            # ── 5. Text-only via WA-JS ────────────────────────────────────────
            if not clean_message:
                return {'success': False, 'error': 'No message content to send'}

            return self._send_text_wajs(jid, clean_message)

        except Exception as e:
            logger.error(f"_send_message_internal error for {phone}: {e}")
            return {'success': False, 'error': str(e)}
        finally:
            if is_temp_file and tmp_media_path and os.path.exists(tmp_media_path):
                try:
                    os.remove(tmp_media_path)
                except Exception:
                    pass

    def _send_text_wajs(self, jid, text):
        """Send a plain text message via WPP.chat.sendTextMessage."""
        try:
            js = """
            async ({jid, text}) => {
                try {
                    await WPP.chat.sendTextMessage(jid, text, { createChat: true });
                    return { success: true };
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            }
            """
            result = self.page.evaluate(js, {'jid': jid, 'text': text})
            if result and result.get('success'):
                logger.info(f"✓ Text sent to {jid} via WA-JS")
                return {'success': True}
            err = result.get('error', 'Unknown error') if result else 'null result'
            logger.error(f"WA-JS text send failed: {err}")
            return {'success': False, 'error': err}
        except Exception as e:
            logger.error(f"_send_text_wajs error: {e}")
            return {'success': False, 'error': str(e)}

    def _send_media_wajs(self, jid, file_path, ext, caption='', original_filename=None):
        """
        Send a media file via WPP.chat.sendFileMessage.
        Reads the file, base64-encodes it, and passes a data URI
        directly to WhatsApp's internal JS API — no DOM or file input needed.
        """
        try:
            # Determine MIME type
            mime_type = MIME_MAP.get(ext)
            if not mime_type:
                guessed, _ = mimetypes.guess_type(f'file.{ext}')
                mime_type = guessed or 'application/octet-stream'

            # Determine WPP media type
            if ext in IMAGE_EXTS:
                media_type = 'image'
            elif ext in VIDEO_EXTS:
                media_type = 'video'
            elif ext in AUDIO_EXTS:
                media_type = 'audio'
            else:
                media_type = 'document'

            # Use original filename if provided, otherwise use basename of file_path
            filename = original_filename or os.path.basename(file_path)

            # Read and encode to base64
            with open(file_path, 'rb') as f:
                raw = f.read()
            b64 = base64.b64encode(raw).decode('utf-8')
            data_uri = f"data:{mime_type};base64,{b64}"

            logger.info(f"Sending {filename} ({mime_type}, {len(raw)} bytes) via WA-JS to {jid}")

            js = """
            async ({jid, dataUri, filename, mimeType, mediaType, caption}) => {
                try {
                    const opts = {
                        type: mediaType,
                        filename: filename,
                        mimetype: mimeType,
                        createChat: true
                    };
                    if (caption) opts.caption = caption;
                    await WPP.chat.sendFileMessage(jid, dataUri, opts);
                    return { success: true };
                } catch (e) {
                    return { success: false, error: e.toString() };
                }
            }
            """
            result = self.page.evaluate(js, {
                'jid': jid,
                'dataUri': data_uri,
                'filename': filename,
                'mimeType': mime_type,
                'mediaType': media_type,
                'caption': caption or ''
            })

            if result and result.get('success'):
                logger.info(f"✓ Media '{filename}' sent via WA-JS")
                return {'success': True}
            err = result.get('error', 'Unknown error') if result else 'null result'
            logger.error(f"WA-JS media send failed: {err}")
            return {'success': False, 'error': err}

        except Exception as e:
            logger.error(f"_send_media_wajs error: {e}")
            return {'success': False, 'error': str(e)}

    # ── Kept for compatibility (no longer primary path) ─────────────────────
    def _attach_and_send_media(self, *args, **kwargs):
        """Legacy stub — media is now sent via WA-JS."""
        return False

    def _send_via_clipboard(self, *args, **kwargs):
        """Legacy stub — clipboard approach replaced by WA-JS."""
        return False

    def _type_caption(self, *args, **kwargs):
        pass

    def _click_send(self):
        pass

    # ──────────────────────────────────────────────────────────────────────────
    # Login / status helpers
    # ──────────────────────────────────────────────────────────────────────────

    def check_login_status(self):
        try:
            if not self.page:
                self.is_logged_in = False
                return False
            for sel in ['div[contenteditable="true"][data-tab="3"]', '#side']:
                try:
                    self.page.wait_for_selector(sel, timeout=3000)
                    self.is_logged_in = True
                    logger.info("Logged into WhatsApp Web")
                    return True
                except Exception:
                    pass
            try:
                self.page.wait_for_selector('canvas[aria-label*="QR"]', timeout=3000)
                self.is_logged_in = False
                return False
            except Exception:
                pass
            self.is_logged_in = 'WhatsApp' in (self.page.title() or '')
            return self.is_logged_in
        except Exception as e:
            logger.error(f"check_login_status: {e}")
            self.is_logged_in = False
            return False
    
    def get_qr_code(self):
        """Capture WhatsApp QR code as base64 image for display in web UI"""
        try:
            if not self.page:
                return {'success': False, 'error': 'Browser not connected. Click Connect first.'}
            
            if self.is_logged_in:
                return {'success': False, 'error': 'Already logged in'}
            
            # Check if page is loaded
            try:
                current_url = self.page.url
                if 'web.whatsapp.com' not in current_url:
                    return {'success': False, 'error': 'Loading WhatsApp Web...'}
            except:
                return {'success': False, 'error': 'Page not ready yet...'}
            
            # Try multiple QR code selectors
            qr_selectors = [
                'canvas[aria-label*="QR"]',
                'canvas[aria-label="Scan me!"]',
                'canvas[role="img"]',
                'div[data-ref] canvas',
                'canvas'
            ]
            
            qr_data = None
            for selector in qr_selectors:
                try:
                    # Check if element exists
                    element = self.page.query_selector(selector)
                    if element:
                        # Try to get QR code
                        qr_data = self.page.evaluate(f'''() => {{
                            const canvas = document.querySelector('{selector}');
                            if (canvas && canvas.width > 100) {{
                                return canvas.toDataURL('image/png');
                            }}
                            return null;
                        }}''')
                        if qr_data and qr_data.startswith('data:image'):
                            logger.info(f"QR code captured using selector: {selector}")
                            return {'success': True, 'qr_code': qr_data}
                except Exception as e:
                    logger.debug(f"Selector {selector} failed: {e}")
                    continue
            
            # If no QR found, check if already logged in
            try:
                is_chat_visible = self.page.query_selector('#side') is not None
                if is_chat_visible:
                    self.is_logged_in = True
                    return {'success': False, 'error': 'Already logged in'}
            except:
                pass
            
            return {'success': False, 'error': 'QR code not visible yet. Please wait...'}
                
        except Exception as e:
            logger.error(f"get_qr_code error: {e}")
            return {'success': False, 'error': f'Error: {str(e)}'}

    # ──────────────────────────────────────────────────────────────────────────
    # Public send API (thread-safe queue)
    # ──────────────────────────────────────────────────────────────────────────

    def send_message(self, phone, message, media_url=None, media_filename=None):
        try:
            self.message_queue.put({'phone': phone, 'message': message, 'media_url': media_url, 'media_filename': media_filename})
            try:
                return self.result_queue.get(timeout=120)
            except queue.Empty:
                return {'success': False, 'error': 'Timeout waiting for send'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    # ──────────────────────────────────────────────────────────────────────────
    # WhatsApp Groups & Participants Grabber
    # ──────────────────────────────────────────────────────────────────────────

    def get_whatsapp_groups(self):
        """Fetch all WhatsApp groups for the logged-in user."""
        try:
            if not self.is_logged_in or not self.page:
                return {'success': False, 'error': 'Not logged into WhatsApp Web'}
            self.message_queue.put({'action': 'get_groups'})
            try:
                return self.result_queue.get(timeout=30)
            except queue.Empty:
                return {'success': False, 'error': 'Timeout fetching WhatsApp groups'}
        except Exception as e:
            logger.error(f"get_whatsapp_groups error: {e}")
            return {'success': False, 'error': str(e)}

    def get_group_participants(self, group_jid):
        """Fetch all participants for a specific WhatsApp group."""
        try:
            if not self.is_logged_in or not self.page:
                return {'success': False, 'error': 'Not logged into WhatsApp Web'}
            self.message_queue.put({'action': 'get_group_participants', 'group_jid': group_jid})
            try:
                return self.result_queue.get(timeout=30)
            except queue.Empty:
                return {'success': False, 'error': 'Timeout fetching group participants'}
        except Exception as e:
            logger.error(f"get_group_participants error: {e}")
            return {'success': False, 'error': str(e)}

    def _fetch_groups_internal(self):
        try:
            wpp_exists = self.page.evaluate("() => typeof window.WPP !== 'undefined'")
            if not wpp_exists:
                self._inject_wajs()

            js = """
            async () => {
                try {
                    let groups = [];

                    // 1. WPP.group.getAllGroups()
                    if (window.WPP && window.WPP.group && typeof window.WPP.group.getAllGroups === 'function') {
                        try {
                            const raw = await window.WPP.group.getAllGroups();
                            if (Array.isArray(raw) && raw.length > 0) {
                                return raw.map(g => ({
                                    id: g.id?._serialized || g.id?.toString() || '',
                                    name: g.name || g.formattedTitle || g.contact?.formattedName || 'Group',
                                    participants_count: g.groupMetadata?.participants?.length || (Array.isArray(g.participants) ? g.participants.length : 0)
                                }));
                            }
                        } catch (e) {
                            console.warn('WPP.group.getAllGroups error:', e);
                        }
                    }

                    // 2. WPP.chat.list({ onlyGroups: true })
                    if (window.WPP && window.WPP.chat && typeof window.WPP.chat.list === 'function') {
                        try {
                            const raw = await window.WPP.chat.list({ onlyGroups: true });
                            if (Array.isArray(raw) && raw.length > 0) {
                                return raw.map(c => ({
                                    id: c.id?._serialized || c.id?.toString() || '',
                                    name: c.name || c.formattedTitle || c.contact?.formattedName || 'Group',
                                    participants_count: c.groupMetadata?.participants?.length || 0
                                }));
                            }
                        } catch (e) {
                            console.warn('WPP.chat.list error:', e);
                        }
                    }

                    // 3. Store.Chat.models fallback
                    if (window.Store && window.Store.Chat && window.Store.Chat.models) {
                        try {
                            const chats = window.Store.Chat.models.filter(c => c.isGroup || (c.id && c.id.server === 'g.us'));
                            return chats.map(c => ({
                                id: c.id?._serialized || c.id?.toString() || '',
                                name: c.formattedTitle || c.name || (c.contact && c.contact.formattedName) || 'Group',
                                participants_count: (c.groupMetadata && c.groupMetadata.participants && c.groupMetadata.participants.length) || 0
                            }));
                        } catch (e) {
                            console.warn('Store.Chat fallback error:', e);
                        }
                    }

                    return groups;
                } catch (err) {
                    return { error: err.toString() };
                }
            }
            """
            res = self.page.evaluate(js)
            if isinstance(res, dict) and 'error' in res:
                return {'success': False, 'error': res['error']}
            return {'success': True, 'groups': res or []}
        except Exception as e:
            logger.error(f"_fetch_groups_internal error: {e}")
            return {'success': False, 'error': str(e)}

    def _fetch_group_participants_internal(self, group_jid):
        try:
            wpp_exists = self.page.evaluate("() => typeof window.WPP !== 'undefined'")
            if not wpp_exists:
                self._inject_wajs()

            js = """
            async (groupJid) => {
                try {
                    let participants = [];

                    // 1. WPP.group.getParticipants
                    if (window.WPP && window.WPP.group && typeof window.WPP.group.getParticipants === 'function') {
                        try {
                            const list = await window.WPP.group.getParticipants(groupJid);
                            if (Array.isArray(list) && list.length > 0) {
                                for (const p of list) {
                                    const phone = p.id?.user || (p.id?._serialized ? p.id._serialized.split('@')[0] : '');
                                    let name = '';
                                    if (window.WPP.contact && typeof window.WPP.contact.get === 'function') {
                                        try {
                                            const c = await window.WPP.contact.get(p.id);
                                            name = c?.name || c?.pushname || c?.shortName || '';
                                        } catch (_) {}
                                    }
                                    if (!name && p.contact) {
                                        name = p.contact.name || p.contact.pushname || '';
                                    }
                                    participants.push({
                                        phone: phone,
                                        name: name || '',
                                        isAdmin: !!p.isAdmin,
                                        isSuperAdmin: !!p.isSuperAdmin
                                    });
                                }
                                if (participants.length > 0) return participants;
                            }
                        } catch (e) {
                            console.warn('WPP.group.getParticipants error:', e);
                        }
                    }

                    // 2. Store.Chat or Store.GroupMetadata fallback
                    if (window.Store && window.Store.Chat) {
                        try {
                            let chat = window.Store.Chat.get ? window.Store.Chat.get(groupJid) : null;
                            if (!chat && window.Store.Chat.models) {
                                chat = window.Store.Chat.models.find(c => (c.id?._serialized || c.id) === groupJid);
                            }
                            if (chat && chat.groupMetadata && chat.groupMetadata.participants) {
                                const pList = chat.groupMetadata.participants.models || chat.groupMetadata.participants;
                                for (const p of pList) {
                                    const phone = p.id?.user || (p.id?._serialized ? p.id._serialized.split('@')[0] : '');
                                    const name = p.contact?.name || p.contact?.pushname || p.contact?.formattedName || '';
                                    participants.push({
                                        phone: phone,
                                        name: name || '',
                                        isAdmin: !!p.isAdmin,
                                        isSuperAdmin: !!p.isSuperAdmin
                                    });
                                }
                                return participants;
                            }
                        } catch (e) {
                            console.warn('Store.GroupMetadata error:', e);
                        }
                    }

                    return participants;
                } catch (err) {
                    return { error: err.toString() };
                }
            }
            """
            res = self.page.evaluate(js, group_jid)
            if isinstance(res, dict) and 'error' in res:
                return {'success': False, 'error': res['error']}
            return {'success': True, 'participants': res or []}
        except Exception as e:
            logger.error(f"_fetch_group_participants_internal error: {e}")
            return {'success': False, 'error': str(e)}

    # ──────────────────────────────────────────────────────────────────────────
    # Campaign management
    # ──────────────────────────────────────────────────────────────────────────

    def start_campaign(self, campaign_id):
        if self.is_running:
            return {'success': False, 'error': 'Another campaign is already running'}
        if not self.is_logged_in:
            return {'success': False, 'error': 'Not logged into WhatsApp Web'}
        if not self.context or not self.page:
            return {'success': False, 'error': 'Browser not connected'}

        self.current_campaign_id = campaign_id
        self.is_running = True
        self.is_paused = False
        self.firebase.update_campaign_status(campaign_id, 'running')

        self.worker_thread = threading.Thread(target=self._campaign_worker, daemon=True)
        self.worker_thread.start()
        return {'success': True, 'message': 'Campaign started'}

    def pause_campaign(self):
        if not self.is_running:
            return {'success': False, 'error': 'No campaign running'}
        self.is_paused = True
        if self.current_campaign_id:
            self.firebase.update_campaign_status(self.current_campaign_id, 'paused')
        return {'success': True, 'message': 'Campaign paused'}

    def resume_campaign(self):
        if not self.is_paused:
            return {'success': False, 'error': 'Campaign not paused'}
        self.is_paused = False
        if self.current_campaign_id:
            self.firebase.update_campaign_status(self.current_campaign_id, 'running')
        return {'success': True, 'message': 'Campaign resumed'}

    def stop_campaign(self):
        if not self.is_running:
            return {'success': False, 'error': 'No campaign running'}
        self.is_running = False
        self.is_paused = False
        if self.current_campaign_id:
            self.firebase.update_campaign_status(self.current_campaign_id, 'stopped')
            self.current_campaign_id = None
        return {'success': True, 'message': 'Campaign stopped'}

    def _campaign_worker(self):
        logger.info(f"Campaign worker started: {self.current_campaign_id}")
        try:
            if not self.page:
                logger.error("No page")
                return

            campaign = self.firebase.get_campaign(self.current_campaign_id)
            campaign_media = None
            campaign_media_filename = None
            if campaign:
                local_path = campaign.get('media_path')
                if local_path and os.path.exists(local_path):
                    campaign_media = local_path
                    campaign_media_filename = campaign.get('media_filename')  # Get original filename
                else:
                    campaign_media = campaign.get('media_url') or local_path
                    campaign_media_filename = campaign.get('media_filename')
            logger.info(f"Campaign media: {campaign_media or 'none'}")

            while self.is_running:
                if self.is_paused:
                    time.sleep(1)
                    continue

                contact = self.firebase.get_next_pending_contact(self.current_campaign_id)
                if not contact:
                    logger.info("Campaign completed")
                    self.firebase.update_campaign_status(self.current_campaign_id, 'completed')
                    break

                self.firebase.mark_contact_sending(self.current_campaign_id, contact['id'])
                result = self.send_message(contact['phone'], contact.get('message', ''), 
                                         media_url=campaign_media, media_filename=campaign_media_filename)

                if result['success']:
                    self.firebase.mark_contact_sent(self.current_campaign_id, contact['id'])
                    logger.info(f"✓ Sent to {contact['phone']}")
                else:
                    self.firebase.mark_contact_failed(self.current_campaign_id, contact['id'], result.get('error', ''))
                    logger.error(f"✗ Failed {contact['phone']}: {result.get('error')}")

                delay = random.randint(Config.MIN_DELAY_SECONDS, Config.MAX_DELAY_SECONDS)
                logger.info(f"Waiting {delay}s…")
                time.sleep(delay)

        except Exception as e:
            logger.error(f"Campaign worker error: {e}")
            if self.current_campaign_id:
                self.firebase.update_campaign_status(self.current_campaign_id, 'stopped')
        finally:
            self.is_running = False
            self.is_paused = False
            self.current_campaign_id = None

    def get_status(self):
        return {
            'is_connected': self.is_connected,
            'is_logged_in': self.is_logged_in,
            'is_running': self.is_running,
            'is_paused': self.is_paused,
            'current_campaign_id': self.current_campaign_id
        }

    def cleanup(self):
        self.is_running = False
        self.is_paused = False
        self.browser_thread_running = False
        if self.browser_thread and self.browser_thread.is_alive():
            self.browser_thread.join(timeout=5)
        self._cleanup_browser()

    def _cleanup_browser(self):
        try:
            if self.context:
                self.context.close()
                self.context = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
            self.browser = None
            self.page = None
            self.is_connected = False
            self.is_logged_in = False
        except Exception as e:
            logger.error(f"_cleanup_browser: {e}")

    def logout(self):
        self.cleanup()
        return {'success': True, 'message': 'Logged out successfully'}
