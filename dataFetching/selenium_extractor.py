import logging, vars
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from lxml import html, etree
from xml.dom.minidom import parseString

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Configure Selenium to use headless Chrome
options = Options()
options.headless = True
service = Service(vars.CHROME_DRIVER_PATH)

class SeleniumExtractor:
    """ Use of selenium model to access some unaccessible pages(sitemaps) """
    @staticmethod
    def from_url(url: str):
        try:
            # Initialize the WebDriver
            driver = webdriver.Chrome(service=service, options=options)
            try:
                # Navigate to the sitemap URL
                driver.get(url)
                # Get the page source
                page_source = driver.page_source
                 # Parse the HTML using BeautifulSoup
                page_content = html.fromstring(page_source)
                # Convert the BeautifulSoup object to a string
                xml_str = etree.tostring(page_content, pretty_print=True, encoding="unicode")
                return xml_str
            
            finally:
                # Close the WebDriver
                driver.quit()

        except Exception as e:
            logging.exception("An error occurred")
