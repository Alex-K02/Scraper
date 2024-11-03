import os, sys
import requests
import logging
from playwright.sync_api import sync_playwright
from .cleaner import Cleaner
import random, time

# Set the global logging level
logging.basicConfig(level=logging.WARNING)

PARENT_DIR = os.path.abspath(os.path.curdir)
sys.path.insert(0, PARENT_DIR)

import vars

class EventScraper:
    def __init__(self, db_handler, ai_module):
        self.cleaner = Cleaner()
        self.db_handler = db_handler
        self.ai_module = ai_module

    def request_page_content(self, url):
        try: 
            response = requests.get(url, headers=vars.headers)
            response.raise_for_status()  # Ensure we notice bad responses
            return response.text
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            logging.info("Attempting to fetch page content using Playwright")
            try:
                response = self.get_page_content(url)
                return response
            except Exception as e:
                logging.error(f"Error occurred while fetching with SeleniumExtractor: {e}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error occurred: {err}")
        return None

    def get_page_content(self, url):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Use headless=True if you don't need the browser to be visible
            page = browser.new_page()
            page.goto(url)
            
            # Simulate scrolling
            page.mouse.wheel(0, random.randint(100, 500))
            time.sleep(random.uniform(1.5, 3.0))

            # Simulate random mouse movement
            page.mouse.move(random.randint(0, 800), random.randint(0, 600))
            time.sleep(random.uniform(1.5, 3.0))

            # Wait for the content to load
            page.wait_for_selector('body')
            content = page.content()
            browser.close()
            return content
        
    def from_url(self, url):
        page_content = self.request_page_content(url)
        if page_content:
            print(f"original size = {len(page_content)}, for {url}")
            if len(page_content) > 230000:
                page_content = self.cleaner.clean([page_content])
                print(f"new size = {len(page_content[0])}")
                if len(page_content) > 230000:
                    print(f"Size for {url} is too big")
        if page_content:
            return page_content
        else:
            print(f"Was not parsed = {url}")