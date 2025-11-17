"""
This is a basic online dashboard to extract and load stock market data from the Polygon API

This file displays the dashboard on the web with dash.

"""

from datetime import datetime, timedelta, date
import dash
from dash import Dash, html, dash_table, dcc, Input, Output, State
import pandas as pd
from get_data import *
import data_base
import json
from dash.dependencies import ALL
import time
    
#This is the class responsible for the dasboard
class Dashboard ():
    def __init__(self, pipeline):
        self.app = Dash()
        self.pipeline = pipeline
        self.user_stock = None
        self.user_date = None
        self.df_daily = None
        self.df_range = None

        # caching tickers list to avoid multiple API calls
        self.cached_tickers = None

        self.layout()
        self.input_callback()
    
    # turning debug mode off to avoid multiple API calls when fetching polygon tickers
    def run(self):
        self.app.run(debug=False)
    
    #Using get_daily_data method and converting to pandas dataframe
    def get_daily_data(self, stock, date):
        data = self.pipeline.get_daily_data(stock, date)
        self.df_daily = pd.DataFrame([data])
        return self.df_daily
    

    def get_historical_data(self, stock):
        data = data_base.query_database(stock)
        columns = ['id', 'ticker', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'created_at']
        df = pd.DataFrame(data, columns=columns)
        return df
    
    def fetch_polygon_tickers(self):
        # loads tickers from JSON file

        if self.cached_tickers:
            return self.cached_tickers
    
        try:
            with open('tickers.json', 'r') as f:
                self.cached_tickers = json.load(f)
                return self.cached_tickers
        
        except FileNotFoundError:
            print("tickers.json not found. Make sure to run fetch_tickers.py first.")
            return []
        
        return self.cached_tickers  


    def input_callback(self):
        #getting input and output
        @self.app.callback(
            Output("output-data", "children"),
            Input("submit-button", "n_clicks"),
            Input({"type": "ticker-button", "index":ALL}, "n_clicks"),
            State("input-stock", "value"),
            State("input-date", "date")
            )
        
        #processing input and putting into get_daily_data method
        def process_input(submit_clicks, database_clicks, input_stock, input_date):
            ctx = dash.callback_context

            if not ctx.triggered:
                return html.Div("", id="no-input")
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if button_id == "submit-button" and input_stock and input_date:

                df = self.get_daily_data(input_stock, input_date)

                row = df.iloc[0].to_dict()

                if df.empty:
                    return [html.Div("No data found for the given stock and/or date.")]

                row = df.iloc[0].to_dict()

                formatted_data = html.Div([
                    html.H3(f"Stock: {input_stock.upper()}"),
                    html.H4(f"Date: {row.get('from', input_date)}"),
                    html.P(f"Open Price: {row.get('open', 'N/A')}"),
                    html.P(f"High Price: {row.get('high', 'N/A')}"),
                    html.P(f"Low Price: {row.get('low', 'N/A')}"),
                    html.P(f"Close Price: {row.get('close', 'N/A')}"),
                    html.P(f"Volume: {row.get('volume', 'N/A')}")
                ])
                return formatted_data

            if button_id.startswith("{"): 
                button_info = json.loads(button_id.replace("'", '"'))
                ticker = button_info['index']
                hist_df = self.get_historical_data(ticker)
                if hist_df.empty:
                    return [html.Div("No historical data found for the selected ticker.")]
                cols = [{"name": c, "id": c} for c in hist_df.columns]
                table = dash_table.DataTable(
                    data=hist_df.to_dict('records'),
                    columns=cols,
                    page_size=10,
                    style_table={'overflowX': 'auto'},
                    style_cell={'textAlign': 'center', 'padding': '6px'}
                )
                return table

            return html.Div("No valid input detected.", id="no-valid-input")

            #to do: add error handling based on if date or sock is missing
        
    #dashboard layout
    def layout(self):
        tickers = data_base.get_all_tickers()
        ticker_buttons = [html.Button(
            ticker, 
            id={'type': 'ticker-button', 'index': ticker}, 
            n_clicks=0, 
            style={'margin': '1px'}
            ) for ticker in tickers
            ]

        available_tickers = self.fetch_polygon_tickers()
        ticker_options = [{'label': ticker, 'value': ticker} for ticker in available_tickers]
 

        self.app.layout = html.Div([
            html.H1("Stock Market Dashboard", id='title'),
            html.Br(),
            html.Div([
                html.Div([
                    html.H3("Quick lookup:"),
                    html.Label("Enter a stock ticker:"), 
                    html.Br(),
                    dcc.Dropdown(
                        id="input-stock",
                        options=ticker_options,
                        placeholder="Example: AAPL",
                        searchable=True,
                        clearable=True,
                        style={'width': '300px'}
                    ),
                    html.Br(),
                    html.Br(),
                    html.Label("Select a Date (yyyy-mm-dd):"),
                    html.Br(),
                    dcc.DatePickerSingle(
                        id="input-date"
                    ),
                    html.Br(),
                    html.Br(),
                    html.Button('Submit', id="submit-button"),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.Br(),
                    html.H3("Historical Database Data:"),
                    html.Div(ticker_buttons),
                ], style={'flex': '1'}),
                html.Div([
                    html.Div(id="output-data"),
                ], style={'flex': '1'}),
            ], style={'display': 'flex'}),
        ])

    def run(self):
        self.app.run(debug=True)

def main():

    pipeline = StockMarketPipeline()

    dashboard = Dashboard(pipeline)

    dashboard.run()
   
if __name__ == "__main__":
    main()



