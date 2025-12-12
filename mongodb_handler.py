from pymongo import MongoClient
import os

class MongoHandler:
    def __init__(self):
        self.client = MongoClient(os.getenv('MONGODB_URL'))
        self.db = self.client['recruitgenie']

    def insert_document(self, collection, data):
        return self.db[collection].insert_one(data).inserted_id

    def close(self):
        self.client.close()

