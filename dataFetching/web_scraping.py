
import vars
#from dataFetching import vars
import requests
import xml.etree.ElementTree as ET
import datetime, re
from dateutil import parser
from datetime import timezone
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import cohere
from news_please.newsplease import NewsPlease 
#from dataFetching.news_please.newsplease import NewsPlease

class WebScraper:
    def tag_splitting(data):
        client = cohere.Client(
            vars.COHERE_API_KEY
        )
        response = client.chat(
            message = f"""You are a language model trained to analyze text and identify important keywords. Your task is to extract a list of the most relevant keywords from the given article. A keyword is defined as a significant word or phrase that represents the main topics or themes of the article. Please provide a list of 10 keywords separated by commas.
                Article: {data}
                Keywords:
                """
        )
        for key in response.text.split(", "):
            print(f"{str.lower(key)}\n")


    def get_robots_txt(self, url: str) -> str:
        '''Robots exclusion standard'''

        robots_url = f"https://{url}/robots.txt"
        response = requests.get(robots_url, headers=vars.headers)
        response.raise_for_status()  # Ensure we notice bad responses
        return response
    

    def parse_robots_txt(self, response: requests.Response) -> RobotFileParser:
        rp = RobotFileParser()
        rp.set_url(response.url)
        try:
            response.encoding = 'utf-8'  # Try utf-8 encoding first
            rp.parse(response.text.splitlines())
            #print(response.text.splitlines())
        except UnicodeDecodeError:
            try:
                response.encoding = 'ISO-8859-1'  # Fallback to ISO-8859-1 encoding
                rp.parse(response.text.splitlines())
            except UnicodeDecodeError:
                response.encoding = 'windows-1252'  # Fallback to windows-1252 encoding
                rp.parse(response.text.splitlines())
        return rp

    def check_sub_map(self, map_url:str) -> list:
        try:
            response = requests.get(map_url)
            response.raise_for_status()  # Raises an HTTPError for bad response
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 403:
                print(f"403 Forbidden Error: Access to {map_url} is restricted.")
            else:
                print(f"HTTP error occurred: {http_err}")

        except Exception as err:
            print(f"An error occurred: {err}")

        
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()
        namespaces = {
            'ns0': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'ns1': 'http://www.google.com/schemas/sitemap-news/0.9'
        }

        sitemap_links = [
            sitemap.find('ns0:loc', namespaces).text
            for sitemap in root.findall('ns0:sitemap', namespaces)
        ]
        
        if not sitemap_links:
            return [map_url]
        else:
            return sitemap_links
        

    def site_map_searching(self, parsed_site_maps:list, site_map_url:str):
        current_date = datetime.datetime.today()
        basic_sitemap = "sitemap.xml"

        if len(parsed_site_maps) == 1:
            parsed_site_maps = self.check_sub_map(parsed_site_maps[0])
            if len(parsed_site_maps) == 1:
                return parsed_site_maps[0]

        for tag in vars.site_maps_tags: 
            for site_map in parsed_site_maps:
                #check for a sub-sitemap
                cleared_map = urlparse(site_map).path
                
                if basic_sitemap in cleared_map:
                    basic_sitemap = site_map

                if re.search(fr'sitemap-{current_date.year:04d}-{current_date.month:02d}\.xml', site_map):
                    return site_map
                
                if tag.search(cleared_map):
                    sub_sitemaps = self.check_sub_map(site_map)
                    if len(sub_sitemaps) == 1:
                        return sub_sitemaps[0]
                    else:
                        return self.site_map_searching(sub_sitemaps, site_map_url)
                
        return self.site_map_searching([basic_sitemap], site_map_url)

    def fetch_and_parse_robots(self, site_map_url: str) -> str:
        response = self.get_robots_txt(site_map_url)
        rp = self.parse_robots_txt(response)
        #check for proper site map
        if rp.site_maps():
            #parsed_site_maps = self.site_map_searching(rp.site_maps(), site_map_url)
            return self.site_map_searching(rp.site_maps(), site_map_url)
        else:
            print("From robot.txt were any links extracted")
            return None


    def analyze_map(self, map:str, last_download:str) -> list:
        last_download = parser.isoparse(last_download)
        
        try:
            response = requests.get(map, headers=vars.headers)
            response.raise_for_status()  # Raises an HTTPError for bad response
        except requests.exceptions.HTTPError as http_err:
            if response.status_code == 403:
                print(f"403 Forbidden Error: Access to {url} is restricted.")
            else:
                print(f"HTTP error occurred: {http_err}")

        except Exception as err:
            print(f"An error occurred: {err}")
        
        tree = ET.ElementTree(ET.fromstring(response.text))
        root = tree.getroot()

        namespaces = {
            'ns0': 'http://www.sitemaps.org/schemas/sitemap/0.9', 
            'ns1': 'http://www.google.com/schemas/sitemap-news/0.9'
        }
        #print(ET.dump(root))
        articles = []
        for url in root.findall('ns0:url', namespaces):
            ##for google add such thing as loc checking for tag="technology" and then sort among them
            link = url.find('ns0:loc', namespaces).text
            news = url.find('ns1:news', namespaces)
            
            if not news:
                news = url
            publication = news.find('ns1:publication', namespaces)
            title = news.find('ns1:title', namespaces).text if publication else 'N/A'
            keywords = news.find('ns1:keywords', namespaces).text.lower() if news.find('ns1:keywords', namespaces) else None

            for pub_date_tag in vars.xml_date_tags:
                if news.find(pub_date_tag, namespaces) is not None:
                    pub_date = parser.isoparse(news.find(pub_date_tag, namespaces).text)

            # Ensure both datetimes are offset-aware (including timezone info)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=timezone.utc)  # Assuming UTC if no timezone info is provided

            if last_download.tzinfo is None:
                last_download = last_download.replace(tzinfo=timezone.utc)  # Assuming UTC if no timezone info is provided

            #checking relevance of the article
            if pub_date > last_download:
                #checking the keywords
                if not keywords or any(elem in vars.article_key_words for elem in keywords):
                    articles.append({
                        "link": link,
                        "pub_date": pub_date,
                        "title": title,
                        "keywords": keywords
                    })
            # else:
            #     #because of the features of sitemap structures
            #     #if the data is less then given no reason to go further
            #     break
        return articles


    def web_scraping(self, site_urls: list):
        index = 0
        articles = []
        for site_link in site_urls:
            print(f"\nFor this site({site_link}) following pages:")
            #use robot file to get to sitemap
            current_site_map = self.fetch_and_parse_robots(site_link)
            return current_site_map
            #analyzing site map
            # latest_article_links = self.analyze_map(current_site_map, "2024-07-18T00:00:00+00:00")
            # for page_link in latest_article_links:
            #     articles.append(NewsPlease.from_url(page_link["link"]))
            #     print(articles[index].title)
            #     index += 1
        
        
def main():
    scraper = WebScraper()
    scraper.web_scraping(vars._tech_websites)

if __name__ == "__main__":
    main()
