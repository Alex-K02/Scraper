# Scraper
This repository includes two main scrapers:

* News Article Scraper
* Event Scraper

## News Article Scraper
The News Article Scraper is based on the [News Please library](https://github.com/fhamborg/news-please), which enables structured article extraction. Here’s how it works:

1. **Accessing robots.txt**:
The scraper reads each target website's [robots.txt file (Learn more about robots.txt)](https://en.wikipedia.org/wiki/Robots.txt) to ensure compliance and obtain site structure details.

2. **Locating Article Pages**:
Using paths from robots.txt, it identifies pages where the latest articles are published.

3. **Extracting Article Links**:
The scraper navigates to these pages, gathering URLs of individual articles.

4. **Parsing HTML Content**:
It then parses each article’s HTML with the News Please library to extract data like title, publication date, author, and main content.

5. **Saving Unique Articles**:
To avoid duplicates, only unique articles are saved after parsing.

_The list of target **websites** is maintained in a separate configuration file._

## Event Scraper

The Event Scraper is designed with an AI-driven approach to identify and extract detailed event information. This scraper is flexible and can interpret various event details. The output is being processed in json format.

_The list of the target **events** is maintained in a separate configuration file._
