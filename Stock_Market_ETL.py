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
        self.base_url = "https://api.polygon.io/v1/open-close"

    def fetch_daily_data(self, symbol, date):

        stockTicker = symbol
        date = date

        url = f"{self.base_url}/{stockTicker}/{date}"

        parameters = {
            "apikey": self.api_key
        }

        daily = requests.get(url, params=parameters)
        data = daily.json()

        return data


def main():
    
    api_key = os.getenv("api_key") 

    pipeline = StockMarketPipeline(api_key)

    daily = pipeline.fetch_daily_data("AAPL", "2025-01-10")
    
    daily_change = daily['close'] - daily['open']

    print(f"Symbol: {daily['symbol']:>13}")
    print(f"Date: {daily['from']:>15}")
    print(f"Open: {daily['open']:>15}")
    print(f"Close: {daily['close']:>14}")
    print (f"change: {daily_change:>13.2f}")
    
   
if __name__ == "__main__":
    main()



