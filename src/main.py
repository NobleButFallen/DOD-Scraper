import os
import logging
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from dotenv import load_dotenv
from scraper.company_scraper import CompanyScraper
from scraper.linkedin_scraper import LinkedInScraper
from validator.data_validator import DataValidator

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    filename=f'logs/scraper_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DODScraper:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    SPREADSHEET_ID = '1ptvIANV6edSeuCrDrdM769Fo4GCDS0gL6qILLgUjp9w'
    
    def __init__(self):
        self.creds = None
        self.service = None
        self.company_scraper = CompanyScraper()
        self.linkedin_scraper = LinkedInScraper()
        self.validator = DataValidator()
        
    def authenticate(self):
        """Handles Google Sheets authentication"""
        if os.path.exists('config/token.json'):
            self.creds = Credentials.from_authorized_user_file('config/token.json', self.SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('config/credentials.json', self.SCOPES)
                self.creds = flow.run_local_server(port=0)
            with open('config/token.json', 'w') as token:
                token.write(self.creds.to_json())
        
        self.service = build('sheets', 'v4', credentials=self.creds)
    
    def read_sheet(self):
        """Reads data from Google Sheet"""
        sheet = self.service.spreadsheets()
        result = sheet.values().get(
            spreadsheetId=self.SPREADSHEET_ID,
            range='A2:D'  # Adjust range as needed
        ).execute()
        return result.get('values', [])
    
    def update_sheet(self, range_name, values):
        """Updates Google Sheet with new data"""
        body = {
            'values': values
        }
        self.service.spreadsheets().values().update(
            spreadsheetId=self.SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
    
    def process_company(self, company_name, poc_name=None):
        """Process a single company to find email and LinkedIn profile"""
        try:
            # Find company email
            email = self.company_scraper.find_email(company_name)
            if email and self.validator.validate_email(email):
                logging.info(f"Found valid email for {company_name}: {email}")
            else:
                email = ''
                logging.warning(f"No valid email found for {company_name}")
            
            # Find LinkedIn profile
            linkedin_url = self.linkedin_scraper.find_profile(company_name, poc_name)
            if linkedin_url and self.validator.validate_linkedin_url(linkedin_url):
                logging.info(f"Found valid LinkedIn profile for {company_name}: {linkedin_url}")
            else:
                linkedin_url = ''
                logging.warning(f"No valid LinkedIn profile found for {company_name}")
            
            return email, linkedin_url
            
        except Exception as e:
            logging.error(f"Error processing {company_name}: {str(e)}")
            return '', ''
    
    def run(self):
        """Main execution flow"""
        try:
            # Authenticate with Google Sheets
            self.authenticate()
            
            # Read current data
            data = self.read_sheet()
            
            # Process each company
            for row_index, row in enumerate(data, start=2):  # start=2 because row 1 is headers
                company_name = row[0] if len(row) > 0 else ''
                poc_name = row[1] if len(row) > 1 else None
                
                if not company_name:
                    continue
                
                logging.info(f"Processing company: {company_name}")
                
                # Find email and LinkedIn profile
                email, linkedin_url = self.process_company(company_name, poc_name)
                
                # Update sheet with new data
                if email or linkedin_url:
                    range_name = f'E{row_index}:F{row_index}'  # Columns E and F for email and LinkedIn
                    values = [[email, linkedin_url]]
                    self.update_sheet(range_name, values)
                    logging.info(f"Updated sheet for {company_name}")
                
        except Exception as e:
            logging.error(f"Error in main execution: {str(e)}")

if __name__ == '__main__':
    scraper = DODScraper()
    scraper.run()