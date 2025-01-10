"""
This program is a data pipeline to extract data from the Alpha Vantage API, transform and analyze the data, then load it into a MySQL database.



"""

import pandas as pd
import requests
import os
from dotenv import load_dotenv

load_dotenv()

class StockMarketPipeline():
    def __init__(self, api_key):
        self.api_key = api_key
        self.url = "https://www.alphavantage.co/query"

    def fetch_daily_data(self, symbol):

        parameters = {
            "function": "TIME_SERIES_DAILY",
            "symbol": symbol,
            "apikey": self.api_key
        }

        daily = requests.get(self.url, params=parameters)
        data = daily.json()
        print(data)


def main():
    
    api_key = os.getenv("api_key") 

    pipeline = StockMarketPipeline(api_key)

    pipeline.fetch_daily_data("AAPL")
    

if __name__ == "__main__":
    main()



