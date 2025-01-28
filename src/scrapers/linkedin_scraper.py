import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
import time

class LinkedInScraper:
    def __init__(self):
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def find_company_linkedin(self, company_name):
        """Search for company's LinkedIn profile using Google search."""
        try:
            search_url = f"https://www.google.com/search?q={company_name}+linkedin+company"
            response = self.session.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find LinkedIn URLs
            search_results = soup.find_all('div', class_='g')
            for result in search_results:
                link = result.find('a')
                if link:
                    url = link['href']
                    if 'linkedin.com/company/' in url.lower():
                        return url
            
            return None
        except Exception as e:
            logging.error(f"Error finding LinkedIn for {company_name}: {str(e)}")
            return None

    def find_poc_linkedin(self, company_name, poc_name):
        """Search for POC's LinkedIn profile using Google search."""
        try:
            search_url = f"https://www.google.com/search?q={poc_name}+{company_name}+linkedin"
            response = self.session.get(search_url, headers=self.headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Find LinkedIn URLs
            search_results = soup.find_all('div', class_='g')
            for result in search_results:
                link = result.find('a')
                if link:
                    url = link['href']
                    if 'linkedin.com/in/' in url.lower():
                        return url
            
            return None
        except Exception as e:
            logging.error(f"Error finding LinkedIn for {poc_name} at {company_name}: {str(e)}")
            return None

    def find_linkedin_profile(self, company_name, poc_name=None):
        """Main method to find LinkedIn profile."""
        try:
            # If POC name is available, try to find their profile first
            if poc_name:
                profile_url = self.find_poc_linkedin(company_name, poc_name)
                if profile_url:
                    return profile_url
            
            # If no POC profile found or no POC name provided, find company profile
            return self.find_company_linkedin(company_name)
            
        except Exception as e:
            logging.error(f"Error in find_linkedin_profile for {company_name}: {str(e)}")
            return None