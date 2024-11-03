import dateutil.parser
import vars
import logging
from dataFetching.web_scraper import WebScraper
from db_executor import DBHandler as DBH
from ai_integration.ai_module import AIModule
import argparse
from dataFetching.event_scraper import EventScraper

import dateutil
from datetime import datetime
import time


class Scraper:
    def __init__(self, dbhandler=None, scraper=None, ai_module=None, event_scraper=None):
        self.dbhandler = dbhandler or DBH(vars.DB_BASIC_CONFIG)
        self.scraper = scraper or WebScraper()
        self.ai_module = ai_module or AIModule(vars.AI_API_KEY)
        self.event_scraper = event_scraper or EventScraper(self.dbhandler, self.ai_module)
        
    def start_program(self, last_working_time: str):
        start_time = time.time()
        last_working_time = dateutil.parser.isoparse(last_working_time)
        
        self.dbhandler.db_creation()
        self.process_events()
        self.process_articles(last_working_time)
        
        print("\nProgram working time =", time.time() - start_time)
        print("\nInformation from all sites and events was successfully fetched")
        
    def process_events(self):
        for event_name, url in vars._event_websites.items():
            try:
                event_data = self.event_scraper.from_url(url)
                json_event_data = self.ai_module.extract_data_from_html(
                    event_data, url, event_name, vars.EVENTS_SCRAPE_PROMPT
                )
                self.dbhandler.insert_event_data(json_event_data, url)
                print(f"Event data successfully processed for {event_name}.")
            except Exception as e:
                print(f"Failed to process event {event_name} from {url}: {e}")
    
    def process_articles(self, last_working_time):
        for idx, url in enumerate(vars._tech_websites, 1):
            try:
                articles = self.scraper.from_url(url, last_working_time)
                if articles:
                    unique_articles = self.dbhandler.is_article_unique(articles)
                    analyzed_articles = self.ai_module.analyze_keywords(unique_articles, DELAY)
                    self.dbhandler.article_data_instertion(analyzed_articles)
                    print(f"Articles from {url} were successfully inserted into the database!")
                print(f"Processed {idx}/{len(vars._tech_websites)} sites.")
            except Exception as e:
                print(f"Failed to process articles from {url}: {e}")
    

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
                    prog='AboutIT',
                    description='This program fetches data from different webistes. The using different techniques it extractes wanted information from the websites and adds it to the database'
                )

parser.add_argument('--sleep', default=300, help="Sleep time between working sessions of the program(in seconds) EXAMPLE (\"300\")")
parser.add_argument('--delay', default=5, help="Delay time between ai requests of the program(in seconds) EXAMPLE (\"5\")")
#add arguments before 
args = parser.parse_args()

DELAY = args.delay
SLEEP_TIME = args.sleep

if __name__ == "__main__":
    #"2024-08-16"
    last_time_working = datetime.today().date().isoformat()
    while True:
        scraper = Scraper()
        scraper.start_program(last_time_working)
        last_time_working = datetime.now().isoformat()
        time.sleep(SLEEP_TIME)
