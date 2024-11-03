import logging
import mysql.connector
from mysql.connector import errorcode
import uuid
import vars
from dateutil import parser

# Set up logging
logging.basicConfig(level=logging.WARNING)

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
        """Function converts fetched from db articles data and converts it to json format"""
        import json
        # Convert the result to a list of dictionaries
        results = [dict(zip(columns, row)) for row in data]
        results_json = json.dumps(results, default=str)
        return results_json
    
    def ensure_valid_size(self, article) -> bool:
        # Helper function to validate size
        def check_field_size(field_name, value, max_size):
            if value and len(value) > max_size:
                logging.warning(f"Size of article {field_name} is larger than allowed. {len(value)} > {max_size}")
                return False
            return True

        # Validate each field based on the defined limits
        for field, max_size in vars.article_table_size_limits.items():
            if not check_field_size(field, getattr(article, field, ""), max_size):
                return False

        return True

    def is_article_unique(self, articles: list) -> list:
        """Checks if the articles are unique by their link."""
        try:
            domain = articles[0].source_domain
            try:
                # Execute a query to select all links from the given domain
                self.cursor.execute(
                    vars.DOMAIN_ARTICLE_EXTRACTION_COMMAND, (domain,)
                )
                logging.info("Successfully executed command")
            except mysql.connector.Error as err:
                logging.error(err)
                return []  # Return empty list on error

            # Fetch all stored links
            stored_links = set(link[0] for link in self.cursor.fetchall())
            
            init_len = len(articles)
            # Filter out non-unique articles
            new_list = [article for article in articles if (article.url not in stored_links) and self.ensure_valid_size(article)]
            print(f"Amount of new artciles is: {len(new_list)}/{init_len}")
            self.connection.commit()
            return new_list
        except mysql.connector.Error as err:
            logging.exception("An error occurred during the operation")
            return []
        

    def is_event_unique(self, link, start, end) -> bool:
        """Checks if the event is unique by its link."""
        try:
            # Execute a query to check if the link exists
            self.cursor.execute(vars.URL_EVENT_EXTRACTION_COMMAND, (link,))
            logging.info("Successfully executed command")

            # Check if any result is returned (meaning the link exists)
            results = self.cursor.fetchall()  # Fetch one result, no need to fetch all
            for result in results:
                if (result[2].year == start.year and result[2].month == start.month and result[2].day == start.day and
        result[3].year == end.year and result[3].month == end.month and result[3].day == end.day):
                    return False
            return True
        except mysql.connector.Error as err:
            logging.error(err)
            return False  # Return False if there's an error during the query
        

    def parse_dates(self, dates):
        event_start_date = None
        event_end_date = None
        
        # If dates is None, return early
        if not dates:
            return event_start_date, event_end_date
        
        # Check if dates is a string
        if isinstance(dates, str):
            # Handle the case where dates contains a range (split by "/")
            if "/" in dates:
                event_start_date, event_end_date = dates.split("/")
            # Handle the case where it's just a single date string
            else:
                event_start_date = dates
                event_end_date = None  # There's no end date in this case

        return event_start_date, event_end_date

    def convert(self, date):
        if "T" in date:
            day, time  = date.split("T")
            if all(char == "0" for char in time):
                return self.convert_to_datetime(day)
        return self.convert_to_datetime(date)
    
    def convert_to_datetime(self, date_str):
        from datetime import datetime
        try:
            # Try to parse the date string using dateutil's parser (more flexible)
            date_obj = parser.parse(date_str)
            print("Parsed with dateutil:", date_obj)
        except Exception as ex1:
            print("Error using dateutil parser:", ex1)
            try:
                # If the above fails, use strptime for specific known formats
                date_obj = datetime.strptime(date_str, "%Y%m%dT%H%M%S%z")
                print("Parsed with strptime:", date_obj)
            except Exception as ex2:
                print("Error using strptime:", ex2)
                return None
        return date_obj
        
    def insert_event_data(self, events, url):
        for event in events:
            event_id = str(uuid.uuid4()) 

            if event.get('event_details'):
                event_details = event.get('event_details') 
            else:
                event_details = event
            
            title = event_details.get("title", "")
            dates = event_details.get("dates", "")
            start, end = self.parse_dates(dates)
            if start and end:
                start = self.convert(start)
                end = self.convert(end)
                # if start < end:
                #     logging.warning(f"Impossible date input for {url}!")

            location = event_details.get("location", "")
            event_type = event_details.get("type", "")

            topics = event_details.get("categories", "")
            if topics:
                result = ""
                for topic in topics:
                    result += topic.lower() + ","
                topics = result
            
            speakers = event_details.get("speakers", "")
            if speakers or speakers == "Speakers or Exhibitors":
                result = ""
                for speaker in speakers:
                    result += speaker + ","
                speakers = result
            else:
                speakers = ""
                

            if event.get('registration_and_information'):
                registration_and_information = event.get('registration_and_information')
            else:
                registration_and_information = event
            link = url
            registration_link = registration_and_information.get("registration_url", "")
            description = registration_and_information.get("description", "")
            price = registration_and_information.get("cost", "")

            sponsors = registration_and_information.get("sponsors", "")
            if sponsors:
                if isinstance(sponsors, list):
                    result = ""
                    for sponsor in sponsors:
                        result += sponsor + ","
                    sponsors = result
            else:
                sponsors = ""
            
            if not(event_type or location) or not topics or not description or not (start and end):
                logging.warning(f"Not full information {url}")
                continue
            if not self.is_event_unique(title, start, end):
                logging.warning(f"This event is already stored {url}")
                continue
            try:
                self.cursor.execute(vars.EVENT_INSERTION_COMMAND, (event_id, title, start, end, location, event_type, topics, speakers, link, registration_link, description, price, sponsors))
                logging.info(f"\nSuccessfully executed command: {vars.ARTICLE_INSERTION_COMMAND}")
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                    logging.error("Something is wrong with your user name or password")
                elif err.errno == errorcode.ER_BAD_DB_ERROR:
                    logging.error("Database does not exist")
                else:
                    logging.error(err)
        self.connection.commit()



    def article_data_instertion(self, articles: list):
        for article in articles:
            article_id = str(uuid.uuid4())
            title = article.title
            link = article.url
            domain = article.source_domain
            description = article.description
            #add an additional criteria that if the year in the title and the year in dates is not correspond, don't add
            main_content = article.maintext

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

    #API functions
    def extract_all_data_from(self, table_name):
        try:
            if table_name in vars.allowed_tables:
                query = f"SELECT * FROM {table_name};"
            else:
                raise ValueError("Invalid table name!")
            
            self.cursor.execute(query)
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