from scrapegraphai.graphs import SmartScraperGraph
import json


class Scraper: 
    def fetch_from_url(self, url:str):
        graph_config = {
            "llm": {
                "api_key": "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",
                "model": "gpt-3.5-turbo",
            }
        }

        # Create the SmartScraperGraph instance
        smart_scraper_graph = SmartScraperGraph(
            prompt="""Please extract the following information from the given news article and format it as a JSON object:
                    1. **Title**: The headline or title of the article.
                    2. **Description**: A brief summary or description of the article.
                    3. **Main Text**: The full body text of the article.
                    4. **Author**: The name of the author(s) of the article.
                    5. **Publication Date**: The date when the article was published.
                    6. **URL**: The web address where the article is published.

                    Format the extracted information as a JSON object with the following structure:

                    {
                    "Title": "Extracted Title Here",
                    "Description": "Extracted Description Here",
                    "Main Text": "Extracted Main Text Here",
                    "Author": "Extracted Author Name Here",
                    "Publication Date": "Extracted Publication Date Here",
                    "URL": "Extracted URL Here"
                    }

                    Please provide the JSON object as the output.
                    """,
            source=url,
            config=graph_config
        )
        result = smart_scraper_graph.run()
        if result:
            print(json.dump(result))


if __name__ == "__main__":
    scraper = Scraper()
    scraper.from_url("https://www.cio.com/article/3479647/making-the-gen-ai-and-data-connection-work.html", vars.SCRAPE_PROMPT)