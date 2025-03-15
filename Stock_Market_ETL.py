"""
This is a basic online dashboard to extract and load stock market data from the Polygon API



"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, date

from dash import Dash, html, dash_table, dcc, Input, Output
import pandas as pd



load_dotenv()

class StockMarketPipeline():
    def __init__(self, api_key):
        self.api_key = api_key
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




class Dashboard ():
    def __init__(self, pipeline):
        self.app = Dash()
        self.pipeline = pipeline
        self.user_stock = None
        self.user_date = None
        self.df_daily = None
        self.df_range = None

        self.layout()
        self.input_callback()
        
    #Using get_daily_data method and converting to pandas dataframe
    def get_daily_data(self, stock, date):
        data = self.pipeline.get_daily_data(stock, date)
        self.df_daily = pd.DataFrame([data])
        return self.df_daily

    
    def input_callback(self):

        #getting input and output
        @self.app.callback(
            Output("data-table", "data"),
            Input("stock-select", "value"),
            Input("date-select", "date")
            )
        
        #processing input and putting into get_daily_data method
        def process_input(input_stock, input_date):
            self.user_stock = input_stock
            self.user_date = input_date

            return self.get_daily_data(self.user_stock, self.user_date).to_dict('records')

    #dashboard layout, convert this to html later for github pages?
    def layout(self):
        self.app.layout = html.Div([
            html.Div("Stock Market Data", id='title'),
            html.Label("Select a stock ticker:"),
            dcc.Dropdown(
                id="stock-select",
                options=["AAPL", "MSFT", "NVDA"],
                value=""
            ),
            html.Label("Select a date (yyyy-mm-dd):"),
            dcc.DatePickerSingle(
                id="date-select"
            ),
            dash_table.DataTable(
                id="data-table",
                data = [],
                page_size=10
            ),
        ])

    def run(self):
        self.app.run_server(debug=True)

def main():
    
    api_key = os.getenv("api_key") 

    pipeline = StockMarketPipeline(api_key)

    dashboard = Dashboard(pipeline)

    dashboard.run()
   
if __name__ == "__main__":
    main()



