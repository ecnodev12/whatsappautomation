import pandas as pd
import re
import logging

logger = logging.getLogger(__name__)

class ExcelService:
    
    @staticmethod
    def normalize_phone(phone):
        """Normalize phone number by removing non-numeric characters and adding country code if needed"""
        from config import Config
        
        if pd.isna(phone):
            return None
        
        # Handle scientific notation from Excel (e.g., 2.437524e+14)
        # Convert to float first, then to int to avoid scientific notation
        try:
            if isinstance(phone, float):
                # If it's a float, convert to int to get full number
                phone = int(phone)
            elif isinstance(phone, str) and ('e+' in phone.lower() or 'e-' in phone.lower()):
                # If it's scientific notation as string, convert via float
                phone = int(float(phone))
        except (ValueError, OverflowError):
            pass
        
        # Convert to string and remove spaces, +, -, (, ), etc.
        phone_str = str(phone).strip()
        phone_clean = re.sub(r'[^\d]', '', phone_str)
        
        if not phone_clean:
            return None
        
        # If number doesn't start with a typical country code (less than 10 digits or starts with certain patterns)
        # and is 10 digits, add default country code
        if len(phone_clean) == 10 and phone_clean[0] in ['6', '7', '8', '9']:
            # Likely an Indian mobile number without country code
            phone_clean = Config.DEFAULT_COUNTRY_CODE + phone_clean
        
        return phone_clean
    
    @staticmethod
    def replace_template(template, name):
        """Replace template variables like {{name}}"""
        if not template or pd.isna(template):
            return ""
        
        result = template.replace('{{name}}', str(name) if not pd.isna(name) else '')
        return result
    
    @staticmethod
    def parse_excel(file_path, message_template=None, allow_empty_message=False):
        """
        Parse Excel/CSV file and extract contacts
        Expected columns: name, phone, message (optional if template provided or allow_empty_message is True)
        """
        try:
            # Read file based on extension
            # IMPORTANT: Read phone as string to prevent scientific notation
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path, dtype={'phone': str})
            else:
                # For Excel files, use converters to force phone column to string
                df = pd.read_excel(file_path, dtype={'phone': str}, converters={'phone': str})
            
            # Convert column names to lowercase for consistency
            df.columns = df.columns.str.lower().str.strip()
            
            # Validate required columns
            if 'phone' not in df.columns:
                raise ValueError("Excel file must contain 'phone' column")
            
            # If no message column, no template, and empty message not allowed, raise error
            if 'message' not in df.columns and not message_template and not allow_empty_message:
                raise ValueError("Excel file must contain 'message' column or provide a message template")
            
            contacts = []
            errors = []
            
            for index, row in df.iterrows():
                row_num = index + 2  # +2 because Excel rows start at 1 and header is row 1
                
                # Get phone
                phone = ExcelService.normalize_phone(row.get('phone'))
                if not phone:
                    errors.append(f"Row {row_num}: Invalid or missing phone number")
                    continue
                
                # Validate phone has minimum length
                if len(phone) < 10:
                    errors.append(f"Row {row_num}: Phone number too short: {phone}")
                    continue
                
                # Get name
                name = row.get('name', '')
                if pd.isna(name):
                    name = ''
                
                # Clean name of zero-width spaces
                name = str(name).replace('\u200b', '').strip()
                
                # Get or generate message
                if message_template:
                    message = ExcelService.replace_template(message_template, name)
                elif 'message' in df.columns:
                    message = row.get('message', '')
                    if pd.isna(message):
                        message = ''
                else:
                    message = ''
                
                # Clean message of zero-width spaces
                clean_msg = str(message).replace('\u200b', '').strip() if message else ''
                
                if not clean_msg and not allow_empty_message:
                    errors.append(f"Row {row_num}: Empty message for phone {phone}")
                    continue
                
                contacts.append({
                    'name': name,
                    'phone': phone,
                    'message': clean_msg
                })
            
            return {
                'success': True,
                'contacts': contacts,
                'errors': errors,
                'total': len(contacts),
                'skipped': len(errors)
            }
            
        except Exception as e:
            logger.error(f"Error parsing Excel file: {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'contacts': [],
                'errors': []
            }
    
    @staticmethod
    def validate_file(filename):
        """Validate file extension"""
        allowed_extensions = {'xlsx', 'csv', 'xls'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
