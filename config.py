import os
from dotenv import load_dotenv

load_dotenv()


polygon_api_key = os.getenv("polygon_api_key")
database_url = os.getenv("database_url")