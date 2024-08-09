import logging
from contextlib import closing
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import html, etree

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
