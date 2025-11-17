# This script is used to fetch a JSON list of ticker symbols from the Polygon API.

import requests
import json
import time
import os
from dotenv import load_dotenv


load_dotenv()

def fetch_by_type(ticker_type):
    url = "https://api.polygon.io/v3/reference/tickers"

    params = {
        "apiKey": os.getenv("polygon_api_key"),
        "market": "stocks",
        "active": "true",
        "type": ticker_type,
        "limit": 1000
    }

    tickers = []
    page = 1

    try:   
        while url:
            print(f"  Page {page} - Requesting: {url[:80]}...")

            if page > 1:
                response = requests.get(url, params={ "apiKey": polygon_api_key })
            else:
                response = requests.get(url, params=params)

            data = response.json()
            print(f"  Status: {response.status_code}")

            if response.status_code == 200 and 'results' in data:

                batch_count = len(data.get('results', []))
                print(f"  Fetched {batch_count} tickers on page {page}")

                for ticker_data in data['results']:
                    ticker = ticker_data['ticker']
                    tickers.append(ticker)

                url = data.get('next_url')

                if url:
                    print(f"  Next page available, waiting 13s...")
                    page += 1
                    time.sleep(13)
                else:
                    print(f"  No more pages for {ticker_type}")
            
            elif response.status_code == 429:
                print(f"  Rate limited! Waiting 60 seconds...")
                time.sleep(60)

            else:
                print(f"API Error for {ticker_type}: {data.get('error', 'Unknown')}")
                break
            
    except Exception as e:
        print(f"Error fetching {ticker_type} tickers: {e}")
        
    return tickers

def fetch_all_tickers():
    
    all_tickers = []

    cs_tickers = fetch_by_type("CS")
    print("Total CS tickers fetched:", len(cs_tickers))

    time.sleep(13)

    etf_tickers = fetch_by_type("ETF")
    print("Total ETF tickers fetched:", len(etf_tickers))

    all_tickers = sorted(list(set(cs_tickers + etf_tickers)))

    with open('tickers.json', 'w') as f:
        json.dump(all_tickers, f)
    
    print("Total tickers fetched:", len(all_tickers))

if __name__ == "__main__":
    fetch_all_tickers()