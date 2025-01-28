import os
import time
from google.oauth2 import service_account
from googleapiclient.discovery import build
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import re

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scraper.log'),
        logging.StreamHandler()
    ]
)

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = '1ptvIANV6edSeuCrDrdM769Fo4GCDS0gL6qILLgUjp9w'

def get_google_sheets_service():
    creds = service_account.Credentials.from_service_account_file(
        'config/credentials.json', scopes=SCOPES)
    return build('sheets', 'v4', credentials=creds)

def find_company_email(company_name):
    """Search for company email using various methods."""
    # Implementation for finding company email
    # This is a placeholder - actual implementation will include web scraping
    pass

def find_linkedin_profile(company_name, poc_name=None):
    """Search for LinkedIn profile of company or POC."""
    # Implementation for finding LinkedIn profile
    # This is a placeholder - actual implementation will include web scraping
    pass

def validate_email(email):
    """Validate if email is a corporate email."""
    if not email:
        return False
    
    # Avoid generic email providers
    generic_domains = ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com']
    domain = email.split('@')[1].lower()
    return domain not in generic_domains

def main():
    try:
        service = get_google_sheets_service()
        sheets = service.spreadsheets()

        # Get the data from the sheet
        result = sheets.values().get(
            spreadsheetId=SPREADSHEET_ID,
            range='Sheet1!A2:E'  # Adjust range as needed
        ).execute()
        rows = result.get('values', [])

        for i, row in enumerate(rows, start=2):  # start=2 because we skip header
            try:
                company_name = row[0]
                poc_name = row[1] if len(row) > 1 else None
                
                logging.info(f"Processing {company_name}")
                
                # Find company email
                email = find_company_email(company_name)
                if email and validate_email(email):
                    # Update email in sheet
                    sheets.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f'Sheet1!F{i}',  # Adjust column as needed
                        valueInputOption='RAW',
                        body={'values': [[email]]}
                    ).execute()
                
                # Find LinkedIn profile
                linkedin = find_linkedin_profile(company_name, poc_name)
                if linkedin:
                    # Update LinkedIn in sheet
                    sheets.values().update(
                        spreadsheetId=SPREADSHEET_ID,
                        range=f'Sheet1!G{i}',  # Adjust column as needed
                        valueInputOption='RAW',
                        body={'values': [[linkedin]]}
                    ).execute()
                
                # Sleep to avoid rate limiting
                time.sleep(2)
                
            except Exception as e:
                logging.error(f"Error processing {company_name}: {str(e)}")
                continue

    except Exception as e:
        logging.error(f"Fatal error: {str(e)}")

if __name__ == "__main__":
    main()