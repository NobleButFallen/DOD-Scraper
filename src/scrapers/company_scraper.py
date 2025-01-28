import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import re
import logging

class CompanyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def find_company_website(self, company_name):
        """Search for company's official website using Google search."""
        try:
            search_url = f"https://www.google.com/search?q={company_name}+official+website"
            response = self.session.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find the first organic result
            search_results = soup.find_all('div', class_='g')
            for result in search_results:
                link = result.find('a')
                if link:
                    url = link['href']
                    # Exclude social media and directory sites
                    if not any(domain in url.lower() for domain in ['facebook.com', 'linkedin.com', 'twitter.com', 'yelp.com']):
                        return url
            
            return None
        except Exception as e:
            logging.error(f"Error finding website for {company_name}: {str(e)}")
            return None

    def extract_email_from_page(self, url):
        """Extract email addresses from a webpage."""
        try:
            response = self.session.get(url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Convert to string to search for emails
            page_text = str(soup)
            
            # Look for email patterns
            email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
            emails = re.findall(email_pattern, page_text)
            
            # Filter out common false positives and non-corporate emails
            valid_emails = [
                email for email in emails
                if not any(domain in email.lower() for domain in ['@example.com', '@gmail.com', '@yahoo.com'])
            ]
            
            return valid_emails[0] if valid_emails else None
            
        except Exception as e:
            logging.error(f"Error extracting email from {url}: {str(e)}")
            return None

    def find_company_email(self, company_name):
        """Main method to find company email."""
        try:
            # First find the company website
            website = self.find_company_website(company_name)
            if not website:
                return None
            
            # Try to find email on main page
            email = self.extract_email_from_page(website)
            if email:
                return email
            
            # Try contact page if it exists
            contact_urls = [
                website + '/contact',
                website + '/contact-us',
                website + '/about-us',
                website + '/about'
            ]
            
            for url in contact_urls:
                try:
                    email = self.extract_email_from_page(url)
                    if email:
                        return email
                except:
                    continue
            
            return None
            
        except Exception as e:
            logging.error(f"Error in find_company_email for {company_name}: {str(e)}")
            return None