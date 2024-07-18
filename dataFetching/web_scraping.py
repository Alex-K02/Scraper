
import vars

import requests
import pandas as pd
import xml.etree.ElementTree as ET
import datetime
from bs4 import BeautifulSoup
from urllib.robotparser import RobotFileParser
import cohere, time
from news_please.newsplease import NewsPlease

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


## Robots exclusion standard
def get_robots_txt(url: str) -> str:
    robots_url = f"https://{url}/robots.txt"
    response = requests.get(robots_url)
    response.raise_for_status()  # Ensure we notice bad responses
    return response

def parse_robots_txt(response: requests.Response) -> RobotFileParser:
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

def fetch_and_parse_robots(site_map_url: str) -> str:
    response = get_robots_txt(site_map_url)
    rp = parse_robots_txt(response)
    #check for proper site map
    for site_map in rp.site_maps():
        cleared_map = site_map.removeprefix("https://").replace(site_map_url, "")
        for tag in vars.site_maps_tags:
            if bool(tag.search(cleared_map)):
                return site_map
    return rp.site_maps()

def analyze_map(map:str, last_download:str) -> list:
    request = requests.get(map)
    if request:
        tree = ET.ElementTree(ET.fromstring(request.text))
    else:
        return "No possible"
    root = tree.getroot()
    namespaces = {'ns0': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'ns1': 'http://www.google.com/schemas/sitemap-news/0.9'}
    
    articles = []
    for url in root.findall('ns0:url', namespaces):
        link = url.find('ns0:loc', namespaces).text
        news = url.find('ns1:news', namespaces)
        pub_date = news.find('ns1:publication_date', namespaces).text if news.find('ns1:publication_date', namespaces).text else 'N/A'
        publication = news.find('ns1:publication', namespaces)
        title = news.find('ns1:title', namespaces).text if publication else 'N/A'
        if not last_download or datetime.datetime.fromisoformat(pub_date) > datetime.datetime.fromisoformat(last_download):
            articles.append({
                "link": link,
                "pub_date": pub_date,
                "title": title
            })
    return articles


def web_scraping(site_urls: list):
    articles = []
    for site_link in site_urls:
        #use robot file to get to sitemap
        current_site_maps = fetch_and_parse_robots(site_link)
        #analyzing site map
        latest_article_links = analyze_map(current_site_maps, "2024-07-18T00:00:00+00:00")
        for index, page_link in enumerate(latest_article_links):
            articles.append(NewsPlease.from_url(page_link["link"]))
            print(articles[index].title)
    #time.sleep(5)   
    #ai analyze and db insertion
        
        
def main():
    web_scraping(vars._tech_websites)

if __name__ == "__main__":
    main()
