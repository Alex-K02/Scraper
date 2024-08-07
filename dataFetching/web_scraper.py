
import vars
from news_please.newsplease import NewsPlease 
import requests, logging
import xml.etree.ElementTree as ET
import datetime, re
from dateutil import parser
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
import cohere
from selenium_extractor import SeleniumExtractor as SE


# Set the global logging level
logging.basicConfig(level=logging.ERROR)

# Set the logging level for urllib3, readability and requests to WARNING to suppress debug and info messages
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("readability.readability").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

logging.getLogger("PIL.TiffImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL.PngImagePlugin").setLevel(logging.WARNING)
logging.getLogger("PIL.Image").setLevel(logging.WARNING)
# Set the logging level for specific loggers to ERROR or CRITICAL to reduce verbosity
logging.getLogger("news_please").setLevel(logging.WARNING)
logging.getLogger("newsplease.crawler.response_decoder").setLevel(logging.ERROR)
logging.getLogger("news_please.newsplease.pipeline.extractor.article_extractor").setLevel(logging.ERROR)
logging.getLogger("newspaper.network").setLevel(logging.ERROR)


class WebScraper:
    def tag_splitting(data):
        client = cohere.Client(
            vars.AI_API_KEY
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
        try: 
            response = requests.get(robots_url, headers=vars.headers)
            response.raise_for_status()  # Ensure we notice bad responses
            return response
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            logging.info("Attempting to fetch robots.txt using SeleniumExtractor")
            try:
                response = SE.from_url(robots_url)
                return response
            except Exception as e:
                logging.error(f"Error occurred while fetching with SeleniumExtractor: {e}")
        except requests.exceptions.RequestException as err:
            logging.error(f"Error occurred: {err}")
        return None


    def parse_robots_txt(self, response: requests.Response) -> RobotFileParser:
        rp = RobotFileParser()
        rp.set_url(response.url)
        try:
            response.encoding = 'utf-8'  # Try utf-8 encoding first
            rp.parse(response.text.splitlines())
        except UnicodeDecodeError:
            try:
                response.encoding = 'ISO-8859-1'  # Fallback to ISO-8859-1 encoding
                rp.parse(response.text.splitlines())
            except UnicodeDecodeError:
                response.encoding = 'windows-1252'  # Fallback to windows-1252 encoding
                rp.parse(response.text.splitlines())
        return rp
    

    def check_sub_map(self, map_url:str) -> list:
        response = self.check_accessibility(map_url)

        if not response:
            try: 
                response = SE.from_url(map_url)
            except Exception as e:
                logging.error(f"Error occurred while fetching with SeleniumExtractor: {e}")
                return [map_url]
        else:
            response = response.text
        
        tree = ET.ElementTree(ET.fromstring(response))
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
        
        
    def check_accessibility(self, url: str):
        try:
            response = requests.get(url, headers=vars.headers)
            response.raise_for_status()  # Raises an HTTPError for bad response
        except requests.exceptions.HTTPError as http_err:
            logging.error(f"HTTP error occurred: {http_err}")
            return None
        except requests.exceptions.RequestException as req_err:
            logging.error(f"Request error occurred: {req_err}")
            return None
        except Exception as err:
            logging.error(f"An error occurred: {err}")
            return None
        return response
        
    def site_map_searching(self, parsed_site_maps:list, site_map_url:str):
        current_date = datetime.datetime.today()
        basic_sitemap = "sitemap.xml"

        if len(parsed_site_maps) == 1:
            parsed_site_maps = self.check_sub_map(parsed_site_maps[0])
            if len(parsed_site_maps) == 1:
                #date time will be date time of the last check
                xml_content = self.analyze_map(parsed_site_maps[0], "2024-07-30T00:00:00+00:00")
                if xml_content is not None:
                    return parsed_site_maps[0]

        for tag in vars.site_maps_tags: 
            for site_map in parsed_site_maps:
                #check for a sub-sitemap
                cleared_map = urlparse(site_map).path
                
                if basic_sitemap in cleared_map:
                    basic_sitemap = site_map

                #includes an edge case for such format: /sitemap-year-month.xml
                if re.search(fr'sitemap-{current_date.year:04d}-{current_date.month:02d}\.xml', site_map):
                    return site_map
                
                if tag.search(cleared_map):
                    #simplifying for other edge cases (like domain.com/2024/sitemap.xml or domain.com/2024-08/sitemap.xml)
                    match = re.search(r'/(?P<year>\d{4})(?:-(?P<month>\d{2}))?', site_map)
                    if match:
                        year = int(match.group('year'))
                        month = int(match.group('month')) if match.group('month') else None
                        if year < current_date.year or (year == current_date.year and month and month < current_date.month):
                            print(f"Skipping {site_map}")
                            continue
                    sub_sitemaps = self.check_sub_map(site_map)
                    if len(sub_sitemaps) == 1:
                        xml_content = self.analyze_map(sub_sitemaps[0], "2024-07-30T00:00:00+00:00")
                        if xml_content:
                            return sub_sitemaps[0]
                    else:
                        return self.site_map_searching(sub_sitemaps, site_map_url)
                
        return self.site_map_searching([basic_sitemap], site_map_url)
    

    def fetch_and_parse_robots(self, site_map_url: str) -> str:
        response = self.get_robots_txt(site_map_url)
        rp = self.parse_robots_txt(response)
        #check for proper site map
        if rp.site_maps():
            return self.site_map_searching(rp.site_maps(), site_map_url)
            #check content of the file
        else:
            print("From robot.txt were any links extracted")
            return None


    def analyze_map(self, map_url:str, last_download:str) -> list:
        last_download = parser.isoparse(last_download)
        response = self.check_accessibility(map_url)
        if not response:
            response = SE.from_url(map_url)
        else:
            response = response.text
        
        tree = ET.ElementTree(ET.fromstring(response))
        root = tree.getroot()

        namespaces = {
            'ns0': 'http://www.sitemaps.org/schemas/sitemap/0.9', 
            'ns1': 'http://www.google.com/schemas/sitemap-news/0.9'
        }

        articles = []
        for url in root.findall('ns0:url', namespaces):
            pub_date = None

            link = url.find('ns0:loc', namespaces).text
            #check that domain is not the case
            if link in map_url:
                continue

            news = url.find('ns1:news', namespaces)
            if not news:
                news = url

            publication = news.find('ns1:publication', namespaces)
            title = news.find('ns1:title', namespaces).text if publication else 'N/A'
            keywords = news.find('ns1:keywords', namespaces).text.lower() if news.find('ns1:keywords', namespaces) else None
            language = news.find('ns1:keywords', namespaces).text if news.find('ns1:keywords', namespaces) else None
            if language and language != "en":
                continue

            for pub_date_tag in vars.xml_date_tags:
                date_tag = news.find(pub_date_tag, namespaces)
                if date_tag is not None:
                    date_text = date_tag.text.strip()
                    try:
                        pub_date = parser.isoparse(date_text)
                        break  # Exit the loop if a valid date is found
                    except ValueError:
                        logging.error(f"Invalid date format found: {date_text} by this site: {map_url}\n")
                        continue
            
            if pub_date is None:
                continue
            
            # Ensure both datetimes are offset-aware (including timezone info)
            if pub_date.tzinfo is None:
                pub_date = pub_date.replace(tzinfo=datetime.timezone.utc)  # Assuming UTC if no timezone info is provided

            if last_download.tzinfo is None:
                last_download = last_download.replace(tzinfo=datetime.timezone.utc)  # Assuming UTC if no timezone info is provided

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
        return articles


    def web_scraping(self, site_urls: list):
        index = 0
        articles = []
        for site_link in site_urls:
            print(f"\nFor this site({site_link}) following pages:")
            #use robot file to get to sitemap
            current_site_map = self.fetch_and_parse_robots(site_link)
            #analyzing site map
            xml_content = self.analyze_map(current_site_map, "2024-08-01T00:00:00+00:00")
            for page_link in xml_content:
                fetched_article = NewsPlease.from_url(page_link["link"])
                if fetched_article:
                    articles.append(fetched_article)
                    print(articles[index].title)
                    index += 1
                else:
                    print("!!!Information from that article couldn't be fetched!!!")
        #ai analyze and db insertion
        
        
def main():
    scraper = WebScraper()
    scraper.web_scraping(vars._tech_websites)

if __name__ == "__main__":
    main()
