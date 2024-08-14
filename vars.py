import re

# DB configuration ###########################################################################
DB_BASIC_CONFIG = {
    "user":"root",
    "password":"password",
    "host":"localhost"
}

DB_EXTENDED_CONFIG = {
    "user":"root",
    "password":"password",
    "host":"localhost",
    "database":"newsapp"
}

create_db = ("CREATE DATABASE IF NOT EXISTS newsapp;")
use_db = ("USE newsapp;")

#TODO: make a hashable password with some preix
user_table = ("""CREATE TABLE IF NOT EXISTS users (
    user_id varchar(60) NOT NULL PRIMARY KEY,
    login varchar(255),
    gmail varchar(255),
    name varchar(255),
    password varchar(255)
);""")

articles_table = ("""CREATE TABLE IF NOT EXISTS articles (
    article_id varchar(60) NOT NULL PRIMARY KEY,
    title varchar(255) NOT NULL UNIQUE,
    link varchar(255) NOT NULL,
    domain varchar(255) NOT NULL,
    description varchar(255),
    main_content text NOT NULL,
    pub_date datetime,
    author varchar(255),
    keywords varchar(255)
);""")

article_keyword_summaries_table = ("""CREATE TABLE IF NOT EXISTS article_keyword_summaries (
    article_id varchar(60) NOT NULL PRIMARY KEY,
    title varchar(255) NOT NULL,
    concepts varchar(255) NOT NULL,
    entities varchar(255) NOT NULL,
    terms varchar(255) NOT NULL,
    action_words varchar(255) NOT NULL,
    sub_terms varchar(255) NOT NULL,
    FOREIGN KEY (article_id) REFERENCES articles(article_id)
);""")

DB_CREATION_COMMANDS = [create_db, use_db, articles_table, user_table, article_keyword_summaries_table]

ARTICLE_INSERTION_COMMAND = """
            INSERT INTO articles (article_id, title, link, domain, description, main_content, pub_date, author)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """

KEYWORDS_INSERTION_COMMAND= """
            INSERT INTO article_keyword_summaries (article_id, title, concepts, entities, terms, action_words, sub_terms)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
            """

ARTICLE_EXTRACTION_COMMAND = "SELECT link FROM articles WHERE domain = %s"

#######################################################################################

# Path to your ChromeDriver executable
CHROME_DRIVER_PATH = '/usr/local/bin/chromedriver'

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

AI_API_KEY = "UKLe0Ywcw1dWEh4kgvAj6OlOzP4ZpPrD0gi36VEN"

## idea for prompt: make a table with criterias something like: 1. main topic 2. sub-topic and so on (i need to normalize output from ai)
KEYWORDS_FILTERING_PROMPT = """Read the following news article and summarize its content by categorizing the key information. Your output should be a Python dictionary where each key corresponds to a category, and its value is a list of relevant keywords or phrases extracted from the article. Adhere to the specified range of keywords for each category.

Categories and Specifications:

Title and Headings (2-4 keywords): Focus on summarizing the main topic and core elements of the article.
Core Concepts (3-5 keywords): Highlight the main ideas or key takeaways from the article.
Entities (3-5 keywords): List the main entities, such as people, organizations, or specific technologies mentioned.
Key Terms (3-5 keywords): Identify specific jargon, technical terms, or critical phrases used in the article.
Action Words (2-4 keywords): Include verbs that describe key actions or processes mentioned in the article.
Subject-Specific Terms (2-4 keywords): Incorporate domain-specific terms that relate to the specific topic discussed.

Please ensure the output adheres to the following Python dictionary structure without any words before and after code:

{
    "Title and Headings": [/* 3-6 keywords in lower case only*/],
    "Core Concepts": [/* 3-5 keywords in lower case only*/],
    "Entities": [/* 3-5 keywords in lower case only*/],
    "Key Terms": [/* 3-5 keywords in lower case only*/],
    "Action Words": [/* 2-4 keywords in lower case only*/],
    "Subject-Specific Terms": [/* 3-6 keywords in lower case only*/]
}
"""

SCRAPE_PROMPT="""Please extract the following information from the given news article and format it as a JSON object:
                    1. **Title**: The headline or title of the article.
                    2. **Description**: A brief summary or description of the article.
                    3. **Main Text**: The full body text of the article.
                    4. **Author**: The name of the author(s) of the article.
                    5. **Publication Date**: The date when the article was published.
                    6. **URL**: The web address where the article is published.

                    Format the extracted information as a JSON object with the following structure:

                    {
                        "title": "Extracted Title Here",
                        "description": "Extracted Description Here",
                        "main Text": "Extracted Main Text Here",
                        "author": "Extracted Author Name Here",
                        "pub_date": "Extracted Publication Date Here",
                        "url": "Extracted URL Here"
                    }

                    Please provide the JSON object as the output.
                """

URLS_EXTRACTION_PROMPT = """Extract all URLs from the provided HTML code and output them as a JSON object with the following structure:
                        {
                        "urls": ["first_url", "second_url", ...]
                        }

                        Return only the JSON code, without any additional text.
                        """

response_delay = 0.2
sleep_time = 300 #seconds

#if url contains one of these it will be skipped
url_stopwords = [
    re.compile(r".*/authors/.*$"),
    re.compile(r".*/deals/.*$"),
    re.compile(r".*/gallery/.*$"),
    re.compile(r".*/health-fitness/.*$")
]

xml_date_tags = [
    "ns1:publication_date",
    "ns0:lastmod"
]

site_maps_tags = [
    re.compile(r".*google.*$"),
    re.compile(r"news(?!.*(archive))"),
    re.compile(r"post-sitemap"),
    re.compile(r"/sitemap-index"),
    re.compile(r"/sitemap_index")
]

#TEST Passed:

#Not full informaiton: https://www.cio.com/article/3486269/ai-adoption-is-inevitable-how-to-balance-innovation-with-security-risks.html
#Not full informaiton: https://www.cio.com/article/3485712/deep-automation-a-cio-weapon-for-turning-disruption-into-opportunity.html
#"iotworldtoday.com", "openai.com",

#TODO: improve analyze map funtion cause (check if the newest article is less than last_download then return [None]) (for example arstechnica,"computerweekly.com","itnews.com.au", no articles from 10.08)
# add filters for a link (check content)
# information couldnt be fetched from techradar
# check cio.com for languages, + bigger description ???
# scmagazine response 404 (site problem)

#check web-pages
# digitaltrends: ERROR:root:1062 (23000): Duplicate entry 'NYT Crossword: answers for Monday, August 12' for key 'articles.title'
# ERROR:root:1062 (23000): Duplicate entry 'NYT Connections: hints and answers for Monday, August 12' for key 'articles.title'
_tech_websites = [
    "futurism.com",
    "blog.google",
    "thehackernews.com",
    "techcrunch.com",
    "arstechnica.com",
    "techrepublic.com",
    "infoworld.com",
    "cio.com",
    "digitaltrends.com",
    "techradar.com",
    "androidcentral.com",
    "readwrite.com",
    "venturebeat.com",
    "9to5mac.com",
    "windowscentral.com",
    "informationweek.com",
    "tomshardware.com",
    "techspot.com",
    "imore.com",
    "cnet.com",
    "gizmodo.com",
    "neowin.net",
    "computerweekly.com",
    "theverge.com",
    "zdnet.com",
    "bgr.com",
    "itnews.com.au",
    "pcgamer.com",
    "itpro.co.uk",
    "sitepoint.com",
    "scmagazine.com",
    "techiexpert.com",
    "wired.com",
    "mashable.com"
]