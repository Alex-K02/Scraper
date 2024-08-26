import dateutil.parser
import vars
import logging
from dataFetching.web_scraper import WebScraper
from db_executor import DBHandler as DBH
from ai_integration.ai_module import AIModule
import argparse

import dateutil
from datetime import datetime
import time


class NewsApp:
    def __init__(self, dbhandler=None, scraper=None, ai_module=None):
        self.dbhandler = dbhandler or DBH(vars.DB_BASIC_CONFIG)
        self.scraper = scraper or WebScraper()
        self.ai_module = ai_module or AIModule(vars.AI_API_KEY)
        
    def start_program(self, last_working_time:str):
        start_time = time.time()
        last_working_time = dateutil.parser.isoparse(last_working_time)
        self.dbhandler.db_creation()
        counter = 0
        for url in vars._tech_websites:
            articles = self.scraper.from_url(url, last_working_time)
            print(f"Articles were successfully fetched from: {url}!")
            if len(articles) > 0:
                articles = self.dbhandler.is_article_unique(articles)
                articles = self.ai_module.analyze_keywords(articles, DELAY)
                self.dbhandler.article_data_instertion(articles)
                print(f"Articles were successfully inserted in table!!!")
            counter += 1
            print(f"{counter}/{len(vars._tech_websites)}")
        print("\nProgram working time = ", time.time() - start_time)
        print("\nInformation from all sites were successfully fetched")
    

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(
                    prog='AboutIT',
                    description='This program fetches data from different webistes. The using different techniques it extractes wanted information from the websites and adds it to the database'
                )

parser.add_argument('--sleep', default=300, help="Sleep time between working sessions of the program(in seconds) EXAMPLE (\"300\")")
parser.add_argument('--delay', default=3, help="Delay time between ai requests of the program(in seconds) EXAMPLE (\"5\")")
#add arguments before 
args = parser.parse_args()

DELAY = args.delay
SLEEP_TIME = args.sleep

if __name__ == "__main__":
    #"2024-08-16"
    last_time_working = datetime.today().date().isoformat()
    while True:
        newsapp = NewsApp()
        newsapp.start_program(last_time_working)
        last_time_working = datetime.now().isoformat()
        time.sleep(SLEEP_TIME)
