import re
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

class CompanyScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

    def find_company_website(self, company_name):
        """Find the official company website using Google search"""
        try:
            search_url = f"https://www.google.com/search?q={company_name}+official+website"
            response = self.session.get(search_url)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find first organic result
            search_results = soup.find_all('div', class_='g')
            for result in search_results:
                link = result.find('a')
                if link:
                    url = link.get('href')
                    # Verify it's a company domain (not social media, directories, etc.)
                    if self._is_company_domain(url, company_name):
                        return url
            return None
        except Exception as e:
            logging.error(f"Error finding website for {company_name}: {str(e)}")
            return None

    def _is_company_domain(self, url, company_name):
        """Verify if the URL likely belongs to the company"""
        if not url:
            return False
        
        # Skip common non-company domains
        skip_domains = ['linkedin.com', 'facebook.com', 'twitter.com', 'instagram.com',
                       'youtube.com', 'bloomberg.com', 'wikipedia.org']
        
        return not any(domain in url.lower() for domain in skip_domains)

    def find_email(self, company_name):
        """Find company email from their website"""
        try:
            website = self.find_company_website(company_name)
            if not website:
                return None

            # Check main page
            response = self.session.get(website)
            email = self._extract_email(response.text)
            if email:
                return email

            # Check contact page
            contact_urls = self._find_contact_pages(website, response.text)
            for contact_url in contact_urls:
                try:
                    response = self.session.get(contact_url)
                    email = self._extract_email(response.text)
                    if email:
                        return email
                except Exception as e:
                    logging.error(f"Error accessing contact page {contact_url}: {str(e)}")

            return None
        except Exception as e:
            logging.error(f"Error finding email for {company_name}: {str(e)}")
            return None

    def _find_contact_pages(self, base_url, html):
        """Find contact page URLs from the main page"""
        soup = BeautifulSoup(html, 'html.parser')
        contact_urls = []
        
        contact_keywords = ['contact', 'about', 'reach']
        for link in soup.find_all('a', href=True):
            href = link.get('href')
            text = link.text.lower()
            
            if any(keyword in text for keyword in contact_keywords):
                full_url = urljoin(base_url, href)
                contact_urls.append(full_url)
        
        return contact_urls

    def _extract_email(self, html):
        """Extract email addresses from HTML content"""
        # Basic email regex pattern
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        
        # Find all email addresses
        emails = re.findall(email_pattern, html)
        
        # Filter out common non-business emails
        filtered_emails = [
            email for email in emails
            if not any(domain in email.lower() 
                      for domain in ['gmail.com', 'yahoo.com', 'hotmail.com', 'outlook.com'])
        ]
        
        return filtered_emails[0] if filtered_emails else None