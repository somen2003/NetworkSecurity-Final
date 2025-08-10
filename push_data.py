import os
import sys
import json
import pandas as pd
import numpy as np
import pymongo
import certifi
from dotenv import load_dotenv

from networksecurity.logging.logger import logging
from networksecurity.exception.exception import NetworkSecurityException

# Load environment variables
load_dotenv()
MONGO_DB_URL = os.getenv("MONGO_DB_URL")
print("MongoDB URL loaded from .env file:", MONGO_DB_URL)

# SSL certificate for secure connection
ca = certifi.where()

class NetworkDataExtract:
    def __init__(self):
        try:
            pass
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def cv_to_json_converter(self, file_path):
        try:
            data = pd.read_csv(file_path)
            data.reset_index(drop=True, inplace=True)
            records = list(json.loads(data.T.to_json()).values())
            return records
        except Exception as e:
            raise NetworkSecurityException(e, sys)

    def insert_data_to_mongodb(self, records, database_name, collection_name):
        try:
            # Connect to MongoDB using the URL and cert
            self.mongo_client = pymongo.MongoClient(MONGO_DB_URL, tlsCAFile=ca)
            
            # Access DB and collection
            self.database = self.mongo_client[database_name]
            self.collection = self.database[collection_name]
            
            # Insert records
            self.collection.insert_many(records)
            return len(records)
        except Exception as e:
            raise NetworkSecurityException(e, sys)

if __name__ == "__main__":
    FILE_PATH = "Network_Data/PhishingData.csv"
    DATABASE = "NetworkSecurity"
    COLLECTION = "PhishingData"

    networkobj = NetworkDataExtract()
    
    records = networkobj.cv_to_json_converter(file_path=FILE_PATH)
    print(records)

    no_of_records = networkobj.insert_data_to_mongodb(records, DATABASE, COLLECTION)
    print(f"Number of records inserted: {no_of_records}")