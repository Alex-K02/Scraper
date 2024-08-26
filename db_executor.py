import logging
import mysql.connector
from mysql.connector import errorcode
import uuid
import vars

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class DBHandler:
    def __init__(self, config):
        self.config = config
        self.connection = None
        self.cursor = None
        self._connect_to_db()
    
    def _connect_to_db(self):
        """Establishes the connection to the database."""
        try:
            self.connection = mysql.connector.connect(**self.config)
            self.cursor = self.connection.cursor()
            logging.info("Database connection established")
        except mysql.connector.Error as err:
            self._handle_mysql_error(err)
            raise  # Re-raise the error if needed
    
    def close_connection(self):
        """Closes the connection to the database."""
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
        logging.info("Database connection closed")

    def _handle_mysql_error(self, err):
        """Handles MySQL errors."""
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            logging.error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            logging.error("Database does not exist")
        else:
            logging.error(err)
    
    def db_creation(self):
        for command in vars.DB_CREATION_COMMANDS:
            try:
                self.cursor.execute(command)
                logging.info(f"Successfully executed command: {command}")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logging.error("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    logging.error("Database does not exist")
                else:
                    logging.error(err)
        self.connection.commit()
    
    def mysql_to_json(self, data, columns:list):
        import json
        # Convert the result to a list of dictionaries
        results = [dict(zip(columns, row)) for row in data]
        results_json = json.dumps(results, default=str)
        return results_json

    def is_article_unique(self, articles: list) -> list:
        """Checks if the articles are unique by their link."""
        try:
            domain = articles[0].source_domain
            try:
                # Execute a query to select all links from the given domain
                self.cursor.execute(
                    vars.ARTICLE_EXTRACTION_COMMAND, (domain,)
                )
                logging.info("Successfully executed command")
            except mysql.connector.Error as err:
                logging.error(err)
                return []  # Return empty list on error

            # Fetch all stored links
            stored_links = set(link[0] for link in self.cursor.fetchall())
            
            init_len = len(articles)
            # Filter out non-unique articles
            new_list = [article for article in articles if article.url not in stored_links]
            print(f"Amount of new artciles is: {len(new_list)}/{init_len}")
            self.connection.commit()
            return new_list
        except mysql.connector.Error as err:
            logging.exception("An error occurred during the operation")
            return []
    
    def get_all_articles(self):
        try:
            self.cursor.execute(vars.ALL_ARTICLE_EXTRACTION_COMMAND)
            # Fetch the column names
            columns = [column[0] for column in self.cursor.description]
            json_articles = self.mysql_to_json(self.cursor.fetchall(), columns)
            self.connection.commit()
            return json_articles
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error(err)
    
    def get_latest_articles(self, last_working_time:str):
        from datetime import datetime
        from dateutil import parser
        try: 
            #formatting from string iso format into sql format
            parsed_time = parser.isoparse(last_working_time)
            formatted_time = parsed_time.strftime('%Y-%m-%d %H:%M:%S')
            last_working_time = datetime.strptime(formatted_time, '%Y-%m-%d %H:%M:%S')

            self.cursor.execute(vars.LATEST_ARTICLE_EXTRACTION_COMMAND, (last_working_time, ))
            # Fetch the column names
            columns = [column[0] for column in self.cursor.description]
            #convert sql to json
            json_articles = self.mysql_to_json(self.cursor.fetchall(), columns)
            self.connection.commit()
            return json_articles
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                logging.error("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                logging.error("Database does not exist")
            else:
                logging.error(err)

    def delete_article(self, article_id):
        try: 
            self.cursor.execute(vars.ARTICLE_DELETION_COMMAND, (article_id, ))
            self.connection.commit()
            return True
        except Exception as e:
            logging.error(f"Error deleting article with id {article_id}: {e}", exc_info=True)
            raise

    def article_data_instertion(self, articles: list):
        for article in articles:
            article_id = str(uuid.uuid4())
            title = article.title
            link = article.url
            domain = article.source_domain
            description = article.description

            main_content = article.maintext
            if len(main_content) > 65535:
                print("Main text size is bigger than possible")
                continue

            pub_date = article.date_publish
            download_date = article.date_download
            
            if article.authors:
                if article.authors[0] == "Written":
                    author = article.authors[1]
                else:
                     author = article.authors[0]
            else:
                author = article.authors

            if not title or not link or not main_content or not pub_date or not author:
                print(f"Not full informaiton: {link}")
                continue

            keywords = []
            if article.keywords:
                for group in article.keywords:
                    keywords.append(','.join(article.keywords[group]))
            else:
                keywords = ""

            try:
                self.cursor.execute(vars.ARTICLE_INSERTION_COMMAND, (article_id, title, link, domain, description, main_content, pub_date, download_date, author))
                self.cursor.execute(vars.KEYWORDS_INSERTION_COMMAND, (article_id, keywords[0], keywords[1], keywords[2], keywords[3], keywords[4], keywords[5]))
                logging.info(f"\nSuccessfully executed command: {vars.ARTICLE_INSERTION_COMMAND}")
                logging.info(f"Successfully executed command: {vars.ARTICLE_INSERTION_COMMAND}")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logging.error("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    logging.error("Database does not exist")
                else:
                    logging.error(err) 
        self.connection.commit()