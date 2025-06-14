import logging
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

class DataEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.driver = None
        self._setup_selenium()

    def _setup_selenium(self):
        """Setup Selenium WebDriver for dynamic content scraping."""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)

    def enrich(self, contacts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Enrich contact data with additional information from web sources.
        
        Args:
            contacts: List of contact dictionaries to enrich
            
        Returns:
            List of enriched contact dictionaries
        """
        enriched_contacts = []
        
        for contact in contacts:
            try:
                enriched_contact = contact.copy()
                
                # Enrich company website if missing
                if not enriched_contact['website'] and enriched_contact['company_name']:
                    enriched_contact['website'] = self._find_company_website(enriched_contact['company_name'])
                
                # Enrich LinkedIn profile if missing
                if not enriched_contact['linkedin'] and enriched_contact['contact_name']:
                    enriched_contact['linkedin'] = self._find_linkedin_profile(
                        enriched_contact['contact_name'],
                        enriched_contact['company_name']
                    )
                
                # Enrich email if missing
                if not enriched_contact['email'] and enriched_contact['website']:
                    enriched_contact['email'] = self._find_email(
                        enriched_contact['website'],
                        enriched_contact['contact_name']
                    )
                
                enriched_contacts.append(enriched_contact)
                
            except Exception as e:
                logging.error(f"Error enriching contact {contact.get('contact_name', 'Unknown')}: {str(e)}")
                enriched_contacts.append(contact)
        
        return enriched_contacts

    def _find_company_website(self, company_name: str) -> str:
        """Find company website using search engine."""
        try:
            search_url = f"https://www.google.com/search?q={company_name}+official+website"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = self.session.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for the first search result
            for result in soup.find_all('a'):
                href = result.get('href', '')
                if href.startswith('http') and not any(x in href for x in ['google.com', 'youtube.com', 'facebook.com']):
                    return href
            
        except Exception as e:
            logging.error(f"Error finding website for {company_name}: {str(e)}")
        
        return ""

    def _find_linkedin_profile(self, name: str, company: str) -> str:
        """Find LinkedIn profile using search."""
        try:
            search_url = f"https://www.google.com/search?q={name}+{company}+site:linkedin.com/in"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = self.session.get(search_url, headers=headers)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for LinkedIn profile in search results
            for result in soup.find_all('a'):
                href = result.get('href', '')
                if 'linkedin.com/in/' in href:
                    return href
            
        except Exception as e:
            logging.error(f"Error finding LinkedIn profile for {name}: {str(e)}")
        
        return ""

    def _find_email(self, website: str, name: str) -> str:
        """Find email address from company website."""
        try:
            if not website:
                return ""
            
            # Visit the contact page
            contact_urls = [
                f"{website}/contact",
                f"{website}/about",
                f"{website}/team",
                f"{website}/people"
            ]
            
            for url in contact_urls:
                try:
                    self.driver.get(url)
                    time.sleep(2)  # Wait for dynamic content
                    
                    # Look for email patterns
                    page_source = self.driver.page_source
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    import re
                    emails = re.findall(email_pattern, page_source)
                    
                    if emails:
                        # Try to find email matching the contact name
                        name_parts = name.lower().split()
                        for email in emails:
                            if any(part in email.lower() for part in name_parts):
                                return email
                        return emails[0]  # Return first email if no name match
                    
                except Exception:
                    continue
            
        except Exception as e:
            logging.error(f"Error finding email for {name} at {website}: {str(e)}")
        
        return ""

    def __del__(self):
        """Cleanup Selenium WebDriver."""
        if self.driver:
            self.driver.quit() 