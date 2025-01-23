"""
This program is a data pipeline to extract data from the Alpha Vantage API, transform and analyze the data, then load it into a MySQL database.



"""

import pandas as pd
import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

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
    
    def print_daily_data(self, data):

        print(f"Symbol: {data['symbol']:>13}")
        print(f"Date: {data['from']:>15}")
        print(f"Open: {data['open']:>15}")
        print(f"Close: {data['close']:>14}")

    def get_data_range(self, symbol, start, end):

        start = datetime.strptime(start, "%Y-%m-%d")
        end = datetime.strptime(end, "%Y-%m-%d")

        current_date = start    
        data = []
        
        while current_date <= end:
            print(current_date)
            data.append(self.fetch_daily_data(symbol, current_date.strftime("%Y-%m-%d")))
            current_date += timedelta(days=1)
        
        return data

        


def main():
    
    api_key = os.getenv("api_key") 

    pipeline = StockMarketPipeline(api_key)

    daily = pipeline.fetch_daily_data("AAPL", "2025-01-10")
    
    daily_change = daily['close'] - daily['open']

    pipeline.print_daily_data(daily)

    print (f"change: {daily_change:>13.2f}")

    print(pipeline.get_data_range("AAPL", "2025-01-06", "2025-01-08"))
    
   
if __name__ == "__main__":
    main()



