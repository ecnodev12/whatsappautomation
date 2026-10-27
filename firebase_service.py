import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from config import Config
import logging

logger = logging.getLogger(__name__)

class FirebaseService:
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(FirebaseService, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """Initialize Firebase Admin SDK"""
        try:
            # Check if already initialized
            firebase_admin.get_app()
            logger.info("Firebase already initialized")
        except ValueError:
            # Initialize Firebase
            cred_dict = {
                "type": "service_account",
                "project_id": Config.FIREBASE_PROJECT_ID,
                "private_key": Config.FIREBASE_PRIVATE_KEY,
                "client_email": Config.FIREBASE_CLIENT_EMAIL,
                "token_uri": "https://oauth2.googleapis.com/token",
            }
            
            cred = credentials.Certificate(cred_dict)
            firebase_admin.initialize_app(cred)
            logger.info("Firebase initialized successfully")
        
        self._db = firestore.client()
    
    @property
    def db(self):
        return self._db
    
    # Campaign Operations
    def create_campaign(self, name, message_template=''):
        """Create a new campaign"""
        campaign_ref = self._db.collection('campaigns').document()
        campaign_data = {
            'name': name,
            'message_template': message_template or '',
            'status': 'draft',
            'total': 0,
            'sent': 0,
            'failed': 0,
            'pending': 0,
            'created_at': firestore.SERVER_TIMESTAMP,
            'started_at': None,
            'completed_at': None,
            'media_url': None,
            'media_filename': None,
            'media_type': None,
            'imagekit_file_id': None,
        }
        campaign_ref.set(campaign_data)
        return campaign_ref.id
    
    def update_campaign_media(self, campaign_id, media_info):
        """Update campaign with ImageKit and local media info"""
        self._db.collection('campaigns').document(campaign_id).update({
            'media_url': media_info.get('media_url'),
            'media_path': media_info.get('media_path'),
            'media_filename': media_info.get('media_filename'),
            'media_type': media_info.get('media_type'),
            'media_ext': media_info.get('media_ext'),
            'imagekit_file_id': media_info.get('imagekit_file_id'),
        })
    
    def get_campaign(self, campaign_id):
        """Get campaign by ID"""
        doc = self._db.collection('campaigns').document(campaign_id).get()
        if doc.exists:
            data = doc.to_dict()
            data['id'] = doc.id
            return data
        return None
    
    def get_all_campaigns(self):
        """Get all campaigns"""
        campaigns = []
        docs = self._db.collection('campaigns').order_by('created_at', direction=firestore.Query.DESCENDING).stream()
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id
            campaigns.append(data)
        return campaigns
    
    def update_campaign(self, campaign_id, updates):
        """Update campaign fields"""
        self._db.collection('campaigns').document(campaign_id).update(updates)
    
    def update_campaign_status(self, campaign_id, status):
        """Update campaign status"""
        updates = {'status': status}
        if status == 'running':
            updates['started_at'] = firestore.SERVER_TIMESTAMP
        elif status in ['completed', 'stopped']:
            updates['completed_at'] = firestore.SERVER_TIMESTAMP
        self.update_campaign(campaign_id, updates)
    
    # Contact Operations
    def add_contacts(self, campaign_id, contacts):
        """Add contacts to campaign"""
        batch = self._db.batch()
        contacts_ref = self._db.collection('campaigns').document(campaign_id).collection('contacts')
        
        count = 0
        for contact in contacts:
            contact_ref = contacts_ref.document()
            contact_data = {
                'name': contact.get('name', ''),
                'phone': contact['phone'],
                'message': contact['message'],
                'status': 'pending',
                'error': None,
                'sent_at': None,
                'attempts': 0
            }
            batch.set(contact_ref, contact_data)
            count += 1
            
            # Commit batch every 500 documents (Firestore limit)
            if count % 500 == 0:
                batch.commit()
                batch = self._db.batch()
        
        # Commit remaining
        if count % 500 != 0:
            batch.commit()
        
        # Update campaign total and pending counts
        self.update_campaign(campaign_id, {
            'total': count,
            'pending': count
        })
        
        return count
    
    def get_contacts(self, campaign_id, status=None, limit=100, offset=0):
        """Get contacts for a campaign"""
        query = self._db.collection('campaigns').document(campaign_id).collection('contacts')
        
        if status:
            query = query.where('status', '==', status)
        
        query = query.limit(limit).offset(offset)
        
        contacts = []
        for doc in query.stream():
            data = doc.to_dict()
            data['id'] = doc.id
            contacts.append(data)
        
        return contacts
    
    def get_next_pending_contact(self, campaign_id):
        """Get next pending contact to send"""
        query = self._db.collection('campaigns').document(campaign_id).collection('contacts')
        query = query.where('status', '==', 'pending').limit(1)
        
        docs = list(query.stream())
        if docs:
            data = docs[0].to_dict()
            data['id'] = docs[0].id
            return data
        return None
    
    def update_contact(self, campaign_id, contact_id, updates):
        """Update contact fields"""
        self._db.collection('campaigns').document(campaign_id).collection('contacts').document(contact_id).update(updates)
    
    def mark_contact_sending(self, campaign_id, contact_id):
        """Mark contact as being sent"""
        self.update_contact(campaign_id, contact_id, {
            'status': 'sending'
        })
    
    def mark_contact_sent(self, campaign_id, contact_id):
        """Mark contact as sent successfully"""
        self.update_contact(campaign_id, contact_id, {
            'status': 'sent',
            'sent_at': firestore.SERVER_TIMESTAMP
        })
        
        # Update campaign counters
        campaign = self.get_campaign(campaign_id)
        if campaign:
            self.update_campaign(campaign_id, {
                'sent': campaign.get('sent', 0) + 1,
                'pending': max(0, campaign.get('pending', 1) - 1)
            })
    
    def mark_contact_failed(self, campaign_id, contact_id, error):
        """Mark contact as failed"""
        contact_ref = self._db.collection('campaigns').document(campaign_id).collection('contacts').document(contact_id)
        contact = contact_ref.get().to_dict()
        attempts = contact.get('attempts', 0) + 1
        
        self.update_contact(campaign_id, contact_id, {
            'status': 'failed',
            'error': error,
            'attempts': attempts
        })
        
        # Update campaign counters
        campaign = self.get_campaign(campaign_id)
        if campaign:
            self.update_campaign(campaign_id, {
                'failed': campaign.get('failed', 0) + 1,
                'pending': max(0, campaign.get('pending', 1) - 1)
            })
    
    def get_campaign_stats(self, campaign_id):
        """Get campaign statistics"""
        campaign = self.get_campaign(campaign_id)
        if not campaign:
            return None
        
        return {
            'total': campaign.get('total', 0),
            'sent': campaign.get('sent', 0),
            'failed': campaign.get('failed', 0),
            'pending': campaign.get('pending', 0),
            'status': campaign.get('status', 'draft')
        }
    
    def restart_campaign(self, campaign_id):
        """Reset all contacts in a campaign to pending status"""
        try:
            campaign = self.get_campaign(campaign_id)
            if not campaign:
                return {'success': False, 'error': 'Campaign not found'}
            
            total = campaign.get('total', 0)
            if total == 0:
                return {'success': False, 'error': 'Campaign has no contacts'}
            
            # Get all contacts in batches and reset them
            contacts_ref = self._db.collection('campaigns').document(campaign_id).collection('contacts')
            
            # Process in batches of 500 (Firestore write limit)
            batch_size = 500
            docs = contacts_ref.limit(batch_size).stream()
            
            reset_count = 0
            while True:
                batch = self._db.batch()
                batch_count = 0
                
                for doc in docs:
                    batch.update(doc.reference, {
                        'status': 'pending',
                        'error': None,
                        'sent_at': None
                    })
                    batch_count += 1
                    reset_count += 1
                
                if batch_count > 0:
                    batch.commit()
                    logger.info(f"Reset {batch_count} contacts (total: {reset_count})")
                
                if batch_count < batch_size:
                    break
                
                # Get next batch
                docs = contacts_ref.limit(batch_size).stream()
            
            # Update campaign counters
            self.update_campaign(campaign_id, {
                'status': 'draft',
                'sent': 0,
                'failed': 0,
                'pending': total,
                'started_at': None,
                'completed_at': None
            })
            
            logger.info(f"Campaign {campaign_id} restarted: {reset_count} contacts reset to pending")
            return {
                'success': True,
                'message': f'Campaign restarted successfully. {reset_count} contacts reset to pending.',
                'reset_count': reset_count
            }
            
        except Exception as e:
            logger.error(f"Error restarting campaign {campaign_id}: {str(e)}")
            return {'success': False, 'error': str(e)}
