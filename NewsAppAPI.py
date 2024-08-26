import vars
from db_executor import DBHandler
from flask import Flask, request
from flask_restful import Api, Resource
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
api = Api(app)

class ArticleTable(Resource):
    def delete(self):
            dbhandler = None
            try:
                dbhandler = DBHandler(vars.DB_EXTENDED_CONFIG)
                if 'id' not in request.args:
                    return {"message": "ID parameter is required"}, 400
                
                article_id = request.args['id']
                # Perform validation to ensure the UUID format is correct
                if len(article_id) != 36:
                    return {"message": "Invalid ID format!"}, 400

                delete_result = dbhandler.delete_article(article_id)
                if delete_result:
                    return {"message": "Successfully deleted"}, 200
                else:
                    return {"message": "Article not found or could not be deleted"}, 404
            except Exception as e:
                logging.error(f"Error deleting all articles: {e}", exc_info=True)
                return {"message": "Internal server error"}, 500
            finally:
                if dbhandler:
                    dbhandler.close_connection()

    def get(self):
        dbhandler = None
        try:
            dbhandler = DBHandler(vars.DB_EXTENDED_CONFIG)
            if 'last_working_time' in request.args:
                last_working_time_str = request.args['last_working_time']
                # Call the function to fetch latest articles using 'last_working_time'
                fetched_articles = dbhandler.get_latest_articles(last_working_time_str)
            else:
                fetched_articles = dbhandler.get_all_articles()
            return fetched_articles, 200
        except Exception as e:
            logging.error(f"Error fetching all articles: {e}", exc_info=True)
            return {"message": "Internal server error"}, 500
        finally:
            if dbhandler:
                dbhandler.close_connection()

api.add_resource(ArticleTable, vars.PATH_RESTAPI)

if __name__ == "__main__":
    app.run(debug=True)