import vars
from dataFetching.web_scraper import WebScraper
from db_executor import DBHandler as DBH
from dateutil import parser

def main():
    last_download = "2024-08-07T00:00:00+00:00"
    last_download = parser.isoparse(last_download)
    DBH.db_creation(vars.DB_BASIC_CONFIG)
    scraper = WebScraper()
    counter = 0
    for url in vars._tech_websites:
        articles = scraper.from_url(url, last_download)
        print(f"Articles were successfully fetched from{url}!")
        DBH.article_data_instertion(vars.DB_EXTENDED_CONFIG, articles, None)
        print(f"Articles were successfully inserted in table!!!")
        counter += 1
        print(f"{counter}/{len(vars._tech_websites)}")
    print("\nInformation from all sites were successfully fetched")
    

if __name__ == "__main__":
    main()