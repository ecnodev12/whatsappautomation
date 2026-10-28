from flask import Flask, render_template, request, jsonify, send_from_directory, Response
import os
import time
import logging
from werkzeug.utils import secure_filename
from config import Config
from firebase_service import FirebaseService
from excel_service import ExcelService
from whatsapp_worker import WhatsAppWorker
from imagekit_service import ImageKitService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = Config.SECRET_KEY
app.config['UPLOAD_FOLDER'] = Config.UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024  # 64MB max file size (for media)

# Ensure upload folder exists
os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)

# Initialize services
try:
    Config.validate()
    firebase_service = FirebaseService()
    whatsapp_worker = WhatsAppWorker()
    imagekit_service = ImageKitService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    raise

# Media extensions allowed for campaign attachments
MEDIA_EXTENSIONS = {
    'image': {'jpg','jpeg','png','gif','webp','mp4','mov','avi','3gp'},
    'document': {'pdf','doc','docx','xls','xlsx','ppt','pptx','txt','zip','rar','7z','csv'},
    'audio': {'mp3','ogg','wav','m4a','aac','flac'},
}
ALL_MEDIA_EXTENSIONS = {ext for exts in MEDIA_EXTENSIONS.values() for ext in exts}

def allowed_file(filename):
    """Check if file extension is allowed for contacts upload"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS

def allowed_media_file(filename):
    """Check if file extension is allowed for campaign media"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_MEDIA_EXTENSIONS

# Routes

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/version')
def version():
    """Version check endpoint"""
    return jsonify({
        'version': '2.0-VNC',
        'vnc_enabled': True,
        'features': ['VNC Browser Viewer', 'Remote Display', 'Full Browser Access']
    })

@app.route('/vnc')
def vnc_viewer():
    """Redirect to noVNC browser viewer"""
    # In production, this will show the browser via VNC
    # Get the current host
    host = request.host.split(':')[0]
    # Redirect to noVNC on port 6080
    return f'''
    <!DOCTYPE html>
    <html>
    <head>
        <title>WhatsApp Browser Viewer</title>
        <style>
            body {{ margin: 0; padding: 20px; font-family: Arial; background: #1e1e1e; color: white; }}
            .container {{ max-width: 100%; margin: 0 auto; }}
            h1 {{ color: #25D366; }}
            .info {{ background: #2d2d2d; padding: 20px; border-radius: 8px; margin: 20px 0; }}
            .btn {{ display: inline-block; padding: 12px 24px; background: #25D366; color: white; 
                    text-decoration: none; border-radius: 6px; margin: 10px 5px; }}
            iframe {{ width: 100%; height: 85vh; border: 2px solid #25D366; border-radius: 8px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🖥️ WhatsApp Browser Viewer</h1>
            <div class="info">
                <p><strong>This is your WhatsApp Web browser running in the cloud!</strong></p>
                <p>You can interact with it just like a local browser:</p>
                <ul>
                    <li>✅ Scan the QR code directly here</li>
                    <li>✅ View messages and chats</li>
                    <li>✅ Watch campaigns run in real-time</li>
                </ul>
            </div>
            <iframe src="http://{host}:6080/vnc.html?autoconnect=true&resize=scale"></iframe>
            <div class="info">
                <a href="/" class="btn">← Back to Dashboard</a>
                <p style="color:#888;font-size:12px;margin-top:10px;">
                    Tip: Click inside the browser viewer to interact. Use your mouse and keyboard normally.
                </p>
            </div>
        </div>
    </body>
    </html>
    '''

@app.route('/api/campaigns', methods=['GET'])
def get_campaigns():
    """Get all campaigns"""
    try:
        campaigns = firebase_service.get_all_campaigns()
        return jsonify({'success': True, 'campaigns': campaigns})
    except Exception as e:
        logger.error(f"Error getting campaigns: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/create', methods=['POST'])
def create_campaign():
    """Create a new campaign"""
    try:
        data = request.get_json()
        name = data.get('name')
        message_template = data.get('message_template', '')
        
        if not name:
            return jsonify({'success': False, 'error': 'Campaign name is required'}), 400
        
        campaign_id = firebase_service.create_campaign(name, message_template)
        
        return jsonify({
            'success': True,
            'campaign_id': campaign_id,
            'message': 'Campaign created successfully'
        })
    except Exception as e:
        logger.error(f"Error creating campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/upload_media', methods=['POST'])
def upload_campaign_media(campaign_id):
    """Upload a media file (image/video/document/audio) to ImageKit and attach URL to campaign"""
    try:
        campaign = firebase_service.get_campaign(campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        if 'media' not in request.files:
            return jsonify({'success': False, 'error': 'No media file provided'}), 400
        
        file = request.files['media']
        media_type = request.form.get('media_type', 'document')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_media_file(file.filename):
            return jsonify({'success': False, 'error': 'Unsupported media file type'}), 400
        
        # Save temporarily to upload to ImageKit
        media_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'media')
        os.makedirs(media_folder, exist_ok=True)
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower() if '.' in filename else ''
        save_name = f"{campaign_id}_media.{ext}"
        save_path = os.path.join(media_folder, save_name)
        file.save(save_path)
        
        # Upload to ImageKit to get a public URL (use original filename for ImageKit)
        ik_result = imagekit_service.upload_file(save_path, filename)
        
        if not ik_result['success']:
            return jsonify({'success': False, 'error': f"ImageKit upload failed: {ik_result.get('error')}"}), 500
        
        media_url = ik_result['url']
        imagekit_file_id = ik_result.get('file_id', '')
        
        # Update campaign record with ImageKit media info and local cache path
        firebase_service.update_campaign_media(campaign_id, {
            'media_url': media_url,
            'media_path': save_path,
            'media_filename': filename,
            'media_type': media_type,
            'media_ext': ext,
            'imagekit_file_id': imagekit_file_id,
        })
        
        logger.info(f"Media uploaded to ImageKit for campaign {campaign_id}: {media_url}")
        return jsonify({
            'success': True,
            'message': f'Media attached: {filename}',
            'media_url': media_url
        })
    except Exception as e:
        logger.error(f"Error uploading media: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>', methods=['GET'])
def get_campaign(campaign_id):
    """Get campaign details"""
    try:
        campaign = firebase_service.get_campaign(campaign_id)
        
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        return jsonify({'success': True, 'campaign': campaign})
    except Exception as e:
        logger.error(f"Error getting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/upload', methods=['POST'])
def upload_contacts(campaign_id):
    """Upload Excel/CSV file with contacts"""
    try:
        # Check if campaign exists
        campaign = firebase_service.get_campaign(campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        # Check if file is present
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': 'Invalid file type. Only .xlsx and .csv are allowed'}), 400
        
        # Save file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], f"{campaign_id}_{filename}")
        file.save(filepath)
        
        # Get message template if provided in form, or fallback to campaign default template
        message_template = request.form.get('message_template') or campaign.get('message_template', '')
        
        has_media = bool(campaign.get('media_url') or campaign.get('media_path'))
        
        # Parse Excel file
        result = ExcelService.parse_excel(filepath, message_template, allow_empty_message=has_media)
        
        # Remove uploaded file
        os.remove(filepath)
        
        if not result['success']:
            return jsonify(result), 400
        
        if len(result['contacts']) == 0:
            return jsonify({
                'success': False,
                'error': 'No valid contacts found in file',
                'errors': result['errors']
            }), 400
        
        # Add contacts to Firebase
        count = firebase_service.add_contacts(campaign_id, result['contacts'])
        
        return jsonify({
            'success': True,
            'message': f'Successfully uploaded {count} contacts',
            'total': count,
            'skipped': result['skipped'],
            'errors': result['errors']
        })
        
    except Exception as e:
        logger.error(f"Error uploading contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/contacts', methods=['GET'])
def get_contacts(campaign_id):
    """Get contacts for a campaign"""
    try:
        status = request.args.get('status')
        limit = int(request.args.get('limit', 100))
        offset = int(request.args.get('offset', 0))
        
        contacts = firebase_service.get_contacts(campaign_id, status, limit, offset)
        
        return jsonify({
            'success': True,
            'contacts': contacts,
            'count': len(contacts)
        })
    except Exception as e:
        logger.error(f"Error getting contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/status', methods=['GET'])
def get_campaign_status(campaign_id):
    """Get campaign status and statistics"""
    try:
        stats = firebase_service.get_campaign_stats(campaign_id)
        
        if not stats:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        logger.error(f"Error getting campaign status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/start', methods=['POST'])
def start_campaign(campaign_id):
    """Start campaign"""
    try:
        # Check campaign exists and has contacts
        campaign = firebase_service.get_campaign(campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404
        
        if campaign.get('total', 0) == 0:
            return jsonify({'success': False, 'error': 'Campaign has no contacts'}), 400
        
        # Start campaign
        result = whatsapp_worker.start_campaign(campaign_id)
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Error starting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/pause', methods=['POST'])
def pause_campaign(campaign_id):
    """Pause campaign"""
    try:
        result = whatsapp_worker.pause_campaign()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error pausing campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/resume', methods=['POST'])
def resume_campaign(campaign_id):
    """Resume campaign"""
    try:
        result = whatsapp_worker.resume_campaign()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error resuming campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/stop', methods=['POST'])
def stop_campaign(campaign_id):
    """Stop campaign"""
    try:
        result = whatsapp_worker.stop_campaign()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error stopping campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/restart', methods=['POST'])
def restart_campaign(campaign_id):
    """Restart campaign - reset all contacts to pending"""
    try:
        # First stop any running campaign
        if whatsapp_worker.is_running:
            whatsapp_worker.stop_campaign()
        
        # Reset campaign in Firebase
        result = firebase_service.restart_campaign(campaign_id)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error restarting campaign: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/connect', methods=['POST'])
def connect_whatsapp():
    """Start WhatsApp Web browser"""
    try:
        result = whatsapp_worker.start_browser()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error connecting to WhatsApp: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/qrcode', methods=['GET'])
def get_qr_code():
    """Get WhatsApp QR code for scanning"""
    try:
        result = whatsapp_worker.get_qr_code()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error getting QR code: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/status', methods=['GET'])
def whatsapp_status():
    """Get WhatsApp connection status"""
    try:
        status = whatsapp_worker.get_status()
        return jsonify({'success': True, 'status': status})
    except Exception as e:
        logger.error(f"Error getting WhatsApp status: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/debug/inspect', methods=['GET', 'POST'])
def debug_inspect():
    """Debug route to inspect current WhatsApp Web DOM state"""
    try:
        def _inspect_fn(page):
            # Inject if not injected
            has_wpp = page.evaluate("() => typeof window.WPP !== 'undefined'")
            if not has_wpp:
                with open('static/wppconnect-wa.js', 'r', encoding='utf-8') as f:
                    page.evaluate(f.read())
            
            info = page.evaluate('''async () => {
                try {
                    const groups = await WPP.group.getAllGroups();
                    if (!groups || groups.length === 0) return { noGroups: true };
                    const g = groups[0];
                    const pList = await WPP.group.getParticipants(g.id);
                    if (!pList || pList.length === 0) return { noParticipants: true };
                    const p = pList[0];
                    
                    let pKeys = Object.keys(p);
                    let pId = p.id ? { user: p.id.user, server: p.id.server, _serialized: p.id._serialized } : null;
                    let pnVal = p.pn ? p.pn.toString() : null;
                    let phoneNumberVal = p.phoneNumber ? p.phoneNumber.toString() : null;
                    
                    let entry = null;
                    try {
                        entry = await WPP.contact.getPnLidEntry(p.id);
                    } catch(e) { entry = { err: e.toString() }; }
                    
                    let cachePn = null;
                    try {
                        if (WPP.whatsapp && WPP.whatsapp.lidPnCache) {
                            const res = WPP.whatsapp.lidPnCache.getPhoneNumber(p.id);
                            cachePn = res ? res.toString() : null;
                        }
                    } catch(e) { cachePn = { err: e.toString() }; }

                    let contactObj = null;
                    try {
                        const c = await WPP.contact.get(p.id);
                        if (c) {
                            contactObj = {
                                id: c.id ? c.id.toString() : null,
                                pnId: c.pnId ? c.pnId.toString() : null,
                                phoneNumber: c.phoneNumber ? c.phoneNumber.toString() : null,
                                userid: c.userid,
                                name: c.name,
                                pushname: c.pushname
                            };
                        }
                    } catch(e) { contactObj = { err: e.toString() }; }

                    return {
                        groupName: g.name,
                        pKeys,
                        pId,
                        pnVal,
                        phoneNumberVal,
                        entry,
                        cachePn,
                        contactObj
                    };
                } catch(e) {
                    return { error: e.toString() };
                }
            }''')
            return {'success': True, 'info': info}
        
        whatsapp_worker.message_queue.put({'action': 'debug', 'fn': _inspect_fn})
        res = whatsapp_worker.result_queue.get(timeout=15)
        return jsonify(res)
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/groups', methods=['GET'])
def get_whatsapp_groups():
    """Fetch all WhatsApp groups for the logged-in user"""
    try:
        result = whatsapp_worker.get_whatsapp_groups()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching WhatsApp groups: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/group/<path:group_jid>/participants', methods=['GET'])
def get_group_participants(group_jid):
    """Fetch participants of a specific WhatsApp group"""
    try:
        result = whatsapp_worker.get_group_participants(group_jid)
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error fetching group participants: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/campaign/<campaign_id>/import_group_contacts', methods=['POST'])
def import_group_contacts(campaign_id):
    """Import contacts directly from one or more WhatsApp groups into a campaign"""
    try:
        campaign = firebase_service.get_campaign(campaign_id)
        if not campaign:
            return jsonify({'success': False, 'error': 'Campaign not found'}), 404

        data = request.get_json() or {}
        group_jids = data.get('group_jids') or []
        if isinstance(group_jids, str):
            group_jids = [group_jids]
        if not group_jids and data.get('group_jid'):
            group_jids = [data.get('group_jid')]

        if not group_jids:
            return jsonify({'success': False, 'error': 'No WhatsApp group selected'}), 400

        exclude_admins = bool(data.get('exclude_admins', False))
        message_template = data.get('message_template') or campaign.get('message_template', '')

        all_contacts = []
        seen_phones = set()
        skipped_count = 0

        for jid in group_jids:
            res = whatsapp_worker.get_group_participants(jid)
            if not res.get('success'):
                logger.warning(f"Could not fetch participants for group {jid}: {res.get('error')}")
                continue

            participants = res.get('participants', [])
            for p in participants:
                if exclude_admins and (p.get('isAdmin') or p.get('isSuperAdmin')):
                    skipped_count += 1
                    continue

                raw_phone = p.get('phone', '')
                normalized = ExcelService.normalize_phone(raw_phone)
                if not normalized or len(normalized) < 10:
                    skipped_count += 1
                    continue

                if normalized in seen_phones:
                    skipped_count += 1
                    continue

                seen_phones.add(normalized)
                contact_name = p.get('name', '').strip()
                msg = message_template
                if '{{name}}' in msg:
                    msg = msg.replace('{{name}}', contact_name if contact_name else '')

                all_contacts.append({
                    'phone': normalized,
                    'name': contact_name,
                    'message': msg
                })

        if not all_contacts:
            return jsonify({
                'success': False,
                'error': 'No valid contacts could be imported from selected group(s)',
                'skipped': skipped_count
            }), 400

        count = firebase_service.add_contacts(campaign_id, all_contacts)
        logger.info(f"Imported {count} contacts from WhatsApp groups into campaign {campaign_id}")

        return jsonify({
            'success': True,
            'message': f'Successfully imported {count} contacts from WhatsApp group(s)',
            'total': count,
            'skipped': skipped_count
        })

    except Exception as e:
        logger.error(f"Error importing group contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/groups/export_csv', methods=['POST'])
def export_group_contacts_csv():
    """Export participants from selected groups as CSV download"""
    try:
        data = request.get_json() or {}
        group_jids = data.get('group_jids') or []
        if isinstance(group_jids, str):
            group_jids = [group_jids]
        if not group_jids and data.get('group_jid'):
            group_jids = [data.get('group_jid')]

        if not group_jids:
            return jsonify({'success': False, 'error': 'No group selected'}), 400

        import csv
        import io
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Phone', 'Name', 'IsAdmin'])

        seen = set()
        for jid in group_jids:
            res = whatsapp_worker.get_group_participants(jid)
            if res.get('success'):
                for p in res.get('participants', []):
                    phone = ExcelService.normalize_phone(p.get('phone', ''))
                    if phone and phone not in seen:
                        seen.add(phone)
                        writer.writerow([phone, p.get('name', ''), 'Yes' if p.get('isAdmin') else 'No'])

        output.seek(0)
        return Response(
            output.getvalue(),
            mimetype='text/csv',
            headers={'Content-Disposition': 'attachment; filename=whatsapp_group_contacts.csv'}
        )
    except Exception as e:
        logger.error(f"Error exporting group contacts: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/whatsapp/logout', methods=['POST'])
def logout_whatsapp():
    """Logout from WhatsApp Web"""
    try:
        result = whatsapp_worker.logout()
        return jsonify(result)
    except Exception as e:
        logger.error(f"Error logging out: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large error"""
    return jsonify({'success': False, 'error': 'File too large. Maximum size is 16MB'}), 413

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({'success': False, 'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'success': False, 'error': 'Internal server error'}), 500

if __name__ == '__main__':
    logger.info(f"Starting Flask application on port {Config.PORT}")
    logger.info(f"Debug mode: {Config.DEBUG}")
    app.run(host='0.0.0.0', port=Config.PORT, debug=Config.DEBUG)
