import os
import sys
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

#auto-detect if running under pytest
if "pytest" in sys.modules:
    import mongomock
    client = mongomock.MongoClient()
else:
    uri = os.getenv("MONGO_URI")
    client = MongoClient(uri, server_api=ServerApi('1'))

db = client.user_db
entries_collection = db["entries"]
projects_collection = db["projects"]