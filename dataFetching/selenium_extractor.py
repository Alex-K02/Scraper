import logging
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from ai_integration.ai_module import AIModule
from lxml import html, etree
import vars

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure Selenium to use headless Chrome
options = Options()
options.headless = True

class SeleniumExtractor:
    """ Use Selenium to access and extract content from pages (e.g., sitemaps) """
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