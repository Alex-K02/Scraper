import vars
import logging
import cohere
import json
import time

class AIModule:
    """This class provides AI integration to the project."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.client = cohere.Client(api_key)

    def from_url(self, url: str, prompt: str) -> str:
        """Generates a response from the AI model based on the provided URL and prompt."""
        try:
            message = f"{prompt}\nHere is a url: {url}\n"
            # Get the response from the client
            response = self.client.chat(message=message)
            # Log and return the response text
            logging.info(f"AI response: {response.text.strip()}")
            return response.text.strip()
        except cohere.CohereError as e:
            # Log detailed error information
            logging.error(f"CohereError occurred: {e.message} | Status: {e.http_status} | Headers: {e.headers}")
            return "An error occurred while processing your request."
        except Exception as e:
            # Catch any other exceptions that might occur
            logging.error(f"Unexpected error: {str(e)}")
            return "An unexpected error occurred."

    def analyze_keywords(self, articles: list, response_delay: int) -> list:
        """Analyzes keywords for a list of articles."""
        try:
            for article in articles:
                try:
                    message = f"{vars.KEYWORDS_FILTERING_PROMPT} News Article:[{article['maintext']}]"
                    # Get the response from the client
                    response = self.client.chat(message=message)
                    # Parse and store the keywords
                    article['keywords'] = json.loads(response.text)
                    time.sleep(response_delay)
                except cohere.CohereError as e:
                    logging.error(f"CohereError occurred: {e.message} | Status: {e.http_status} | Headers: {e.headers}")
                    return "An error occurred while processing your request."
            return articles
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return "An unexpected error occurred."

    def extract_urls_from_sitemap(self, html: str) -> list:
        """Extracts URLs from the provided sitemap HTML."""
        try:
            message = f"HTML code:[{html}]"
            # Get the response from the client
            response = self.client.chat(message=message)
            # Parse the URLs from the response
            urls = json.loads(response.text.strip())["urls"]
            response = [{"link": url} for url in urls]
            return response
        except cohere.CohereError as e:
            logging.error(f"CohereError occurred: {e.message} | Status: {e.http_status} | Headers: {e.headers}")
            return "An error occurred while processing your request."
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return "An unexpected error occurred."
