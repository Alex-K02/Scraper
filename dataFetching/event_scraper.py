import os, sys
import json
import re
import requests
import logging
from playwright.sync_api import sync_playwright
from cleaner import Cleaner
import random, time
from selenium_extractor import SeleniumExtractor
from db_executor import DBHandler

PARENT_DIR = os.path.abspath(os.path.curdir)
sys.path.insert(0, PARENT_DIR)

import vars
from ai_integration.ai_module import AIModule


class PlayWrightScraper:
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

def main():
    cleaner = Cleaner()
    aimodule = AIModule(api_key=vars.AI_API_KEY)
    play_wright_scraper = PlayWrightScraper()
    db_handler = DBHandler(vars.DB_EXTENDED_CONFIG)

    prompt_response = []

    i = 1
    for event_name, url in vars._event_websites.items():
        page_content = play_wright_scraper.request_page_content(url)
        if page_content:
            print(f"original size = {len(page_content)}, {i}/{len(vars._event_websites)}, {url}")
            if len(page_content) > 230000:
                page_content = cleaner.clean([page_content])
                print(f"new size = {len(page_content[0])}")
                if len(page_content) > 230000:
                    print(f"{i}/{len(vars._event_websites)}")
        if page_content:
            json_event_data = aimodule.extract_data_from_html(page_content, url, event_name, vars.ONE_MORE_PROMPT)
            prompt_response.append(json_event_data)
            db_handler.insert_event_data(json_event_data, url)
        else:
            print(f"Was not parsed = {i}/{len(vars._event_websites)}")
        i += 1

    print("Fetching is done")
    

main()