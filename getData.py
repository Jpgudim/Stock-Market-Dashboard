"""
This is a basic online dashboard to extract and load stock market data from the Polygon API.

This file calls the API to retrieve data.

"""

import requests
from config import polygon_api_key

#Class that handles the data from the Polygon API
class StockMarketPipeline():
    def __init__(self):
        self.api_key = polygon_api_key
        self.base_url = "https://api.polygon.io/v1/open-close"

    #Retrieve daily data from API
    def get_daily_data(self, symbol, date):

        stockTicker = symbol
        date = date

        url = f"{self.base_url}/{stockTicker}/{date}"

        parameters = {
            "apikey": self.api_key
        }

        daily = requests.get(url, params=parameters)
        data = daily.json()

        return data