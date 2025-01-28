import logging
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager

class LinkedInScraper:
    def __init__(self):
        self.setup_driver()

    def setup_driver(self):
        """Set up Chrome WebDriver with appropriate options"""
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.wait = WebDriverWait(self.driver, 10)

    def find_profile(self, company_name, poc_name=None):
        """Find LinkedIn profile for company or POC"""
        try:
            if poc_name:
                return self._find_poc_profile(company_name, poc_name)
            return self._find_company_profile(company_name)
        except Exception as e:
            logging.error(f"Error finding LinkedIn profile for {company_name}: {str(e)}")
            return None
        finally:
            self.driver.quit()

    def _find_company_profile(self, company_name):
        """Find company's LinkedIn profile"""
        try:
            # Search on Google to avoid LinkedIn rate limiting
            self.driver.get(f"https://www.google.com/search?q=site:linkedin.com/company/ {company_name}")
            time.sleep(2)  # Wait for results to load
            
            # Find first LinkedIn company result
            results = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div.g')
            ))
            
            for result in results:
                try:
                    link = result.find_element(By.CSS_SELECTOR, 'a')
                    url = link.get_attribute('href')
                    if 'linkedin.com/company/' in url:
                        return url
                except NoSuchElementException:
                    continue
            
            return None
        except Exception as e:
            logging.error(f"Error finding company LinkedIn profile for {company_name}: {str(e)}")
            return None

    def _find_poc_profile(self, company_name, poc_name):
        """Find POC's LinkedIn profile"""
        try:
            # Search on Google to avoid LinkedIn rate limiting
            search_query = f"site:linkedin.com/in/ {poc_name} {company_name}"
            self.driver.get(f"https://www.google.com/search?q={search_query}")
            time.sleep(2)  # Wait for results to load
            
            # Find first LinkedIn profile result
            results = self.wait.until(EC.presence_of_all_elements_located(
                (By.CSS_SELECTOR, 'div.g')
            ))
            
            for result in results:
                try:
                    link = result.find_element(By.CSS_SELECTOR, 'a')
                    url = link.get_attribute('href')
                    if 'linkedin.com/in/' in url:
                        return url
                except NoSuchElementException:
                    continue
            
            return None
        except Exception as e:
            logging.error(f"Error finding POC LinkedIn profile for {poc_name} at {company_name}: {str(e)}")
            return None