import logging
import requests
from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin, urlparse

class DataEnricher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })

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
            # Search for company website
            search_url = f"https://www.google.com/search?q={company_name}+official+website"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for company website in search results
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    url = href.split('/url?q=')[1].split('&')[0]
                    if self._is_valid_company_website(url, company_name):
                        return url
            
        except Exception as e:
            logging.error(f"Error finding website for {company_name}: {str(e)}")
        
        return ""

    def _find_linkedin_profile(self, name: str, company: str) -> str:
        """Find LinkedIn profile URL."""
        try:
            # Search for LinkedIn profile
            search_query = f"{name} {company} site:linkedin.com/in/"
            search_url = f"https://www.google.com/search?q={search_query}"
            response = self.session.get(search_url, timeout=10)
            soup = BeautifulSoup(response.text, 'lxml')
            
            # Look for LinkedIn profile in search results
            for link in soup.find_all('a'):
                href = link.get('href', '')
                if href.startswith('/url?q='):
                    url = href.split('/url?q=')[1].split('&')[0]
                    if 'linkedin.com/in/' in url:
                        return url
            
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
                    response = self.session.get(url, timeout=10)
                    soup = BeautifulSoup(response.text, 'lxml')
                    
                    # Look for email patterns
                    email_pattern = r'[\w\.-]+@[\w\.-]+\.\w+'
                    emails = re.findall(email_pattern, str(soup))
                    
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

    def _is_valid_company_website(self, url: str, company_name: str) -> bool:
        """Check if URL is a valid company website."""
        try:
            # Parse URL
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            
            # Check if domain contains company name
            company_words = company_name.lower().split()
            return any(word in domain for word in company_words)
            
        except Exception:
            return False 