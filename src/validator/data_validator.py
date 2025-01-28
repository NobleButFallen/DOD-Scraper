import re
import logging
import validators

class DataValidator:
    def __init__(self):
        self.common_email_domains = [
            'gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com',
            'aol.com', 'icloud.com', 'mail.com'
        ]

    def validate_email(self, email):
        """Validate email address format and domain"""
        try:
            # Basic format validation
            if not email or not isinstance(email, str):
                return False

            # Check email format
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if not re.match(email_pattern, email):
                return False

            # Extract domain
            domain = email.split('@')[1].lower()

            # Check if it's not a common personal email domain
            if domain in self.common_email_domains:
                logging.warning(f"Email {email} uses common personal domain")
                return False

            return True
        except Exception as e:
            logging.error(f"Error validating email {email}: {str(e)}")
            return False

    def validate_linkedin_url(self, url):
        """Validate LinkedIn profile URL format"""
        try:
            # Basic URL validation
            if not url or not isinstance(url, str):
                return False

            # Check if it's a valid URL
            if not validators.url(url):
                return False

            # Check if it's a LinkedIn URL
            if not ('linkedin.com/in/' in url.lower() or 'linkedin.com/company/' in url.lower()):
                return False

            return True
        except Exception as e:
            logging.error(f"Error validating LinkedIn URL {url}: {str(e)}")
            return False

    def validate_company_name(self, name):
        """Validate company name format"""
        try:
            if not name or not isinstance(name, str):
                return False

            # Remove special characters and check length
            cleaned_name = re.sub(r'[^a-zA-Z0-9\s]', '', name)
            if len(cleaned_name.strip()) < 2:
                return False

            return True
        except Exception as e:
            logging.error(f"Error validating company name {name}: {str(e)}")
            return False