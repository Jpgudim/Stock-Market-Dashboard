"""
This is a basic online dashboard to extract and load stock market data from the Polygon API.

This file handles the interaction with the database.

"""

import psycopg2
from config import database_url
from getData import StockMarketPipeline
from datetime import date, timedelta
import time

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


def populate_database(ticker, pastDays):
    conn = get_connection()
    cursor = conn.cursor()

    pipeline = StockMarketPipeline()

    endDate = date.today()
    currentDate = endDate - timedelta(days=1)

    for day in range(pastDays):
        
        dateString = currentDate.strftime('%Y-%m-%d')
    
        api_data = pipeline.get_daily_data(ticker, dateString)

        cursor.execute("""
            INSERT INTO stock_prices (ticker, date, open_price, high_price, low_price, close_price, volume)
            VALUES (%s, %s, %s, %s, %s, %s, %s)     
        """, (
            ticker, 
            currentDate, 
            api_data.get('open'), 
            api_data.get('high'), 
            api_data.get('low'), 
            api_data.get('close'), 
            api_data.get('volume') 
        ))

        currentDate = currentDate - timedelta(days=1)

        #API limit is 5 requests per minute
        time.sleep(15) 

    conn.commit()
    cursor.close()
    conn.close()
    print ("Data added successfully")

if __name__ == "__main__":
    get_connection()
    #create_table()
    populate_database("AAPL", 2)
