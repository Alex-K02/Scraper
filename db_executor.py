import logging
import mysql.connector
from mysql.connector import errorcode
import uuid
import vars

# Set up logging
logging.basicConfig(level=logging.DEBUG)

class DBHandler:
    
    def db_creation(config):
        commands = vars.DB_CREATION_COMMANDS
        try:
            # Establish the database connection
            with mysql.connector.connect(**config) as conn:
                with conn.cursor() as cursor:
                    for command in commands:
                        try:
                            cursor.execute(command)
                            logging.info(f"Successfully executed command: {command}")
                        except mysql.connector.Error as err:
                            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                                logging.error("Something is wrong with your user name or password")
                            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                                logging.error("Database does not exist")
                            else:
                                logging.error(err)
                    conn.commit()
        except mysql.connector.Error as err:
            logging.exception("An error occurred while connecting to the database")
    
    def article_data_instertion(config, articles: list, keywords:str):
        try:
            with mysql.connector.connect(**config) as conn:
                with conn.cursor() as cursor:
                    for article in articles:
                        article_id = str(uuid.uuid4())
                        title = article.title
                        link = article.url
                        description = article.description
                        main_content = article.maintext
                        pub_date = article.date_publish
                        author = article.authors[0] if article.authors else article.authors
                        if not title or not link or not main_content or not pub_date or not author:
                            print(f"Not full informaiton: {link}")
                            continue
                        if keywords:
                            keywords = ', '.join(article.keywords)  # Assuming keywords is a list
                        else:
                            keywords = ""

                        command = vars.ARTICLE_INSERTION_COMMAND
                        try:
                            cursor.execute(command, (article_id, title, link, description, main_content, pub_date, author, keywords))
                            logging.info(f"Successfully executed command: {command}")
                        except mysql.connector.Error as err:
                            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                                logging.error("Something is wrong with your user name or password")
                            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                                logging.error("Database does not exist")
                            else:
                                logging.error(err) 
                    conn.commit()
        except mysql.connector.Error as err:
            logging.exception("An error occurred while connecting to the database")