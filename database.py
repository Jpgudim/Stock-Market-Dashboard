"""
This is a basic online dashboard to extract and load stock market data from the Polygon API.

This file handles the database connection.

"""

import psycopg2
from config import database_url

def test_connection():

    conn = psycopg2.connect(database_url)
                
    print("Connection successful")
        
    conn.close()

if __name__ == "__main__":
    test_connection()