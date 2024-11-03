import os, sys
import logging
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import html, etree


PARENT_DIR = os.path.abspath(os.path.curdir)
sys.path.insert(0, PARENT_DIR)

import vars
from ai_integration.ai_module import AIModule

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure Selenium to use headless Chrome
options = webdriver.ChromeOptions()
#options.add_argument('--headless')
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

class SeleniumExtractor:
    """ Use Selenium to access and extract content from pages (e.g., sitemaps) """

    def __init__(self, chrome_driver_path: str):
        self.chrome_driver_path = chrome_driver_path

    @staticmethod
    def from_url(url: str, chrome_driver_path: str) -> str:
        try:
            with closing(webdriver.Chrome(service=Service(chrome_driver_path), options=options)) as driver:
                driver.get(url)
                page_source = driver.page_source
                page_content = html.fromstring(page_source)
                xml_str = etree.tostring(page_content, pretty_print=True, encoding="unicode")
                return xml_str

        except Exception as e:
            logging.exception(f"An error occurred while processing the URL: {url}")
            return ""

    def extract_urls_from_html(url:str, chrome_driver_path:str):
        try:
            with closing(webdriver.Chrome(service=Service(chrome_driver_path), options=options)) as driver:
                driver.get(url)
                page_source = driver.page_source
                ai_module = AIModule(vars.AI_API_KEY)
                urls = ai_module.extract_urls_from_sitemap(page_source)
                return urls
        except Exception as e:
            logging.exception(f"An error occurred while processing the URL: {url}")
            return ""
        
    def extract_page_content(self, url:str):
        try:
            with closing(webdriver.Chrome(service=Service(self.chrome_driver_path), options=options)) as driver:
                driver.get(url)
                page_source = driver.page_source
                return page_source
        except Exception as e:
            logging.exception(f"An error occurred while processing the URL: {url}")
            return ""