"""
This is a basic online dashboard to extract and load stock market data from the Polygon API

To Do:

1. Error checking for ticker input (no caps, ticker doesn't exist, etc.)
2. Error checking for ticker input (weekend, market closed)

3. Get historical data for stock
4. Make data more clean
5. Make dashboard look nice

"""

import requests
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta, date

from dash import Dash, html, dash_table, dcc, Input, Output, State
import pandas as pd

load_dotenv()


#Class that handles the data from the Polygon API
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
    
#This is the class responsible for the dasboard
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
            Input("submit-button", "n_clicks"),
            State("input-stock", "value"),
            State("input-date", "date")
            )
        
        #processing input and putting into get_daily_data method
        def process_input(n_clicks, input_stock, input_date):
            
            #don't process if submit button is not clicked
            if n_clicks is None:
                return []
            
            self.user_stock = input_stock
            self.user_date = input_date

            #collect the data if stock ticker and date are provided
            if input_stock and input_date:
                return self.get_daily_data(self.user_stock, self.user_date).to_dict('records')
            
            return []
        
    #dashboard layout
    def layout(self):
        self.app.layout = html.Div([
            html.H1("Stock Market Dashboard", id='title'),

            html.Label("Enter a stock ticker:"), 
            
            html.Br(),

            dcc.Input(
                id="input-stock",
                type="text",
                placeholder="Example: AAPL"
            ),

            html.Br(),
            html.Br(),

            html.Label("Select a date (yyyy-mm-dd):"),

            html.Br(),

            dcc.DatePickerSingle(
                id="input-date"
            ),

            html.Br(),
            html.Br(),

            html.Button('submit', id="submit-button"),

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



