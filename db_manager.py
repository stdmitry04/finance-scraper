from pymongo import MongoClient
import config

def get_db_connection():
    client = MongoClient(config.MONGO_URI)
    db = client[config.DB_NAME]
    return db

def save_articles(collection_name, articles):
    db = get_db_connection()
    collection = db[collection_name]
    collection.insert_many(articles)
