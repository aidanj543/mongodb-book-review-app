from pymongo.errors import PyMongoError

from database import client

try:
    client.admin.command("ping")
    print("Connected to MongoDB!")
except PyMongoError as e:
    print(f"Failed to connect to MongoDB: {e}")