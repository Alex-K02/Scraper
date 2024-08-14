import vars
from dataFetching.web_scraper import WebScraper
from db_executor import DBHandler as DBH
from ai_integration.ai_module import AIModule
from dateutil import parser
from datetime import datetime
import time


class NewsApp:
    def __init__(self, dbhandler=None, scraper=None, ai_module=None):
        self.dbhandler = dbhandler or DBH(vars.DB_BASIC_CONFIG)
        self.scraper = scraper or WebScraper()
        self.ai_module = ai_module or AIModule(vars.AI_API_KEY)
        
    def start_program(self, last_working_time:str):
        start_time = time.time()
        last_working_time = parser.isoparse(last_working_time)
        self.dbhandler.db_creation()
        counter = 0
        for url in vars._tech_websites:
            articles = self.scraper.from_url(url, last_working_time)
            print(f"Articles were successfully fetched from: {url}!")
            if len(articles) > 0:
                self.dbhandler.is_article_unique(articles)
                articles = self.ai_module.analyze_keywords(articles)
                self.dbhandler.article_data_instertion(articles)
                print(f"Articles were successfully inserted in table!!!")
                counter += 1
            print(f"{counter}/{len(vars._tech_websites)}")
        print("\nProgram working time = ", time.time() - start_time)
        print("\nInformation from all sites were successfully fetched")
    

if __name__ == "__main__":
    last_time_working = datetime.today().isoformat()

    while True:
        newsapp = NewsApp()
        newsapp.start_program(last_time_working)
        last_time_working = datetime.now().isoformat()
        time.sleep(vars.sleep_time)
