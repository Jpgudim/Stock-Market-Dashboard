"""
This is a basic online dashboard to extract and load stock market data from the Polygon API

This file displays the dashboard on the web with dash.

"""

from datetime import datetime, timedelta, date
import dash
from dash import Dash, html, dash_table, dcc, Input, Output, State
import pandas as pd
from getData import *
from config import polygon_api_key
import database
    
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
    

    def get_historical_data(self, stock):
        data = database.query_database(stock)
        columns = ['id', 'ticker', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'created_at']
        df = pd.DataFrame(data, columns=columns)
        return df

    def input_callback(self):

        #getting input and output
        @self.app.callback(
            Output("data-table", "data"),
            Input("submit-button", "n_clicks"),
            Input("database-button", "n_clicks"),
            State("input-stock", "value"),
            State("input-date", "date")
            )
        
        #processing input and putting into get_daily_data method
        def process_input(submit_clicks, database_clicks, input_stock, input_date):
            ctx = dash.callback_context

            if not ctx.triggered or not input_stock:
                return []
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if button_id == "submit-button" and input_stock and input_date:

                return self.get_daily_data(input_stock, input_date).to_dict('records')
            
            elif button_id == "database-button" and input_stock:

                return self.get_historical_data(input_stock).to_dict('records')
            
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
            html.Button('Show database', id="database-button"),

            dash_table.DataTable(
                id="data-table",
                data = [],
                page_size=10
            ),

        ])

    def run(self):
        self.app.run_server(debug=True)

def main():

    pipeline = StockMarketPipeline()

    dashboard = Dashboard(pipeline)

    dashboard.run()
   
if __name__ == "__main__":
    main()



