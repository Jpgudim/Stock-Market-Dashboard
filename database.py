"""
This is a basic online dashboard to extract and load stock market data from the Polygon API.

This file handles the database connection.

"""

import psycopg2
from config import database_url

def get_connection():
    conn = psycopg2.connect(database_url)
    return conn
                        
def create_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS stock_prices (
            id SERIAL PRIMARY KEY,
            ticker VARCHAR(5),
            date DATE,
            open_price DECIMAL(10, 2),
            high_price DECIMAL(10, 2),
            low_price DECIMAL(10, 2),
            close_price DECIMAL(10,2),
            volume BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(ticker, date)
        );
    """)
    
    conn.commit()

    cursor.close()
    conn.close()
    print ("Table created successfully")

if __name__ == "__main__":
    get_connection()
    create_table()