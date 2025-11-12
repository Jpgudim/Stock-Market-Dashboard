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
        data = database.query_database(stock)
        columns = ['id', 'ticker', 'date', 'open_price', 'high_price', 'low_price', 'close_price', 'volume', 'created_at']
        df = pd.DataFrame(data, columns=columns)
        return df
    
    def fetch_polygon_tickers(self):
        
        if self.cached_tickers:
            return self.cached_tickers

        all_tickers = []

        try: 

            cs_tickers = self.fetch_by_type("CS")
            all_tickers.extend(cs_tickers)

            time.sleep(13)

            etf_tickers = self.fetch_by_type("ETF")
            all_tickers.extend(etf_tickers)

            self.cached_tickers = sorted(all_tickers)
            return all_tickers
    
        except Exception as e:
            print(f"Error fetching tickers: {e}")
            return []
        
    def fetch_by_type(self, ticker_type):

        url = "https://api.polygon.io/v3/reference/tickers"

        params = {
            "apiKey": polygon_api_key,
            "market": "stocks",
            "active": "true",
            "type": ticker_type,
            "limit": 1000
        }

        tickers = []

        try:   
            response = requests.get(url, params=params)
            data = response.json()

            print(f"Status Code: {response.status_code}")
            print(f"Response keys: {data.keys()}")

            if response.status_code == 200 and 'results' in data:
                for ticker_data in data['results']:
                    ticker = ticker_data['ticker']
                    tickers.append(ticker)

            else:
                print(f"API Error for {ticker_type}: {data.get('error', 'Unknown')}")

        except Exception as e:
            print(f"Error fetching {ticker_type} tickers: {e}")
                
        return tickers

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
        tickers = database.get_all_tickers()
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



