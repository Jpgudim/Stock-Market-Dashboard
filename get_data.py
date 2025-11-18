"""
This is a basic online dashboard to extract and load stock market data from the Polygon API.

This file calls the API to retrieve data.

"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

#Class that handles the data from the Polygon API
class StockMarketPipeline():
    def __init__(self):
        self.api_key = os.getenv("polygon_api_key")
        self.base_url = "https://api.polygon.io/v1/open-close"

    #Retrieve daily data from API
    def get_daily_data(self, symbol, date):

        url = f"{self.base_url}/{symbol}/{date}"

        parameters = {
            "apikey": self.api_key
        }

        try:
            response = requests.get(url, params=parameters, timeout=10)
            response.raise_for_status
                
            data = response.json()

            if data.get('status') == 'ERROR':
                print(f"API Error: {data.get('error', 'Unknown error')}")
                return None
            
            return data
        
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {symbol} on {date}: {e}")
            return None
        
        except ValueError as e:
            print(f"Invalid JSON response: {e}")
            return None