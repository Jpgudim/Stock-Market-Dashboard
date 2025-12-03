"""
This is a basic online dashboard to extract and load stock market data from the Polygon API

This file displays the dashboard on the web with dash.

"""

from datetime import datetime, timedelta, date
import dash
from dash import Dash, html, dash_table, dcc, Input, Output, State
import pandas as pd
from get_data import *
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

        # caching tickers list to avoid multiple API calls
        self.cached_tickers = None

        self.layout()
        self.input_callback()
    
    def get_daily_data(self, stock, date):
        #Using get_daily_data method and converting to pandas dataframe

        data = self.pipeline.get_daily_data(stock, date)

        # Return empty DataFrame on error
        if data is None or data.get('status') == 'ERROR':
            return pd.DataFrame()  

        self.df_daily = pd.DataFrame([data])
        return self.df_daily

    def get_most_recent_data(self, stock, requested_date):
        #Fallback to get the most recent available data before the requested date

        requested_dt = datetime.strptime(requested_date, '%Y-%m-%d')

        #Trying up to 7 days back
        for days_back in range(0, 8):
            fallback_date = requested_dt - timedelta(days=days_back)
            fallback_date_str = fallback_date.strftime('%Y-%m-%d')
        
            df = self.get_daily_data(stock, fallback_date_str)
        
            if not df.empty and df.iloc[0].get('open') is not None:
                row = df.iloc[0].to_dict()
            
                formatted_data = html.Div([
                    html.Div([
                        html.H3(f"{stock.upper()}", style={
                            'color': '#2c3e50',
                            'marginBottom': '5px',
                            'fontSize': '28px',
                            'fontWeight': '600'
                        }),
                        html.P(f"{row.get('from', fallback_date_str)}", style={
                            'color': '#7f8c8d',
                            'marginTop': '0',
                            'fontSize': '16px',
                            'marginBottom': '15px'
                        }),
                        html.Div([
                            html.P("No data available for the requested date. Showing most recent data.", style={
                                'color': '#e67e22',
                                'fontSize': '14px',
                                'backgroundColor': '#fef5e7',
                                'padding': '10px',
                                'borderRadius': '5px',
                                'marginBottom': '20px',
                                'border': '1px solid #f9e79f'
                            })
                        ]),
                    ], style={'borderBottom': '2px solid #3498db', 'paddingBottom': '15px', 'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span("Open", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('open', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#2c3e50',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#ecf0f1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                            html.Div([
                                html.Span("High", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('high', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#27ae60',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#eafaf1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                        ], style={'display': 'flex', 'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Div([
                                html.Span("Low", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('low', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#e74c3c',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#fadbd8',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                            html.Div([
                                html.Span("Close", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('close', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#2c3e50',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#ecf0f1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                        ], style={'display': 'flex', 'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Span("Volume", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                            html.Div(f"{row.get('volume', 'N/A'):,}", style={
                                'fontSize': '20px',
                                'fontWeight': '600',
                                'color': '#8e44ad',
                                'marginTop': '5px'
                            })
                        ], style={
                            'backgroundColor': '#f4ecf7',
                            'padding': '15px',
                            'borderRadius': '8px',
                            'margin': '5px'
                        }),
                    ])
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                })
                return formatted_data
        return html.Div([
            html.Div([
                html.H3(f"{stock.upper()}", style={
                    'color': '#2c3e50',
                    'marginBottom': '10px'
                }),
                html.P(f"No data found for {requested_date} or the previous 7 days.", style={
                    'color': '#e74c3c',
                    'fontSize': '16px'
                })
            ], style={
                'backgroundColor': '#fadbd8',
                'padding': '20px',
                'borderRadius': '10px',
                'border': '1px solid #e74c3c'
            })
        ])

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
            [Output("output-data", "children"),
             Output("date-picker-container", "style")],
            [Input("submit-button", "n_clicks"),
             Input("calendar-button", "n_clicks")],
            [State("input-stock", "value"),
             State("input-date", "date"),
             State("date-picker-container", "style")]
            )
        
        #processing input and putting into get_daily_data method
        def process_input(submit_clicks, calendar_clicks, input_stock, input_date, current_style):
            ctx = dash.callback_context

            if not ctx.triggered:
                return html.Div("", id="no-input"), {'display': 'none'}
            
            button_id = ctx.triggered[0]['prop_id'].split('.')[0]

            if button_id == "calendar-button":
                if current_style.get('display') == 'none':
                    new_style = {
                        'display': 'block',
                        'position': 'absolute',
                        'top': '45px',
                        'right': '0',
                        'zIndex': '1000',
                        'backgroundColor': 'white',
                        'padding': '10px',
                        'borderRadius': '8px',
                        'boxShadow': '0 4px 12px rgba(0,0,0,0.15)'
                    }
                else:
                    new_style = {'display': 'none'}
                return dash.no_update, new_style

            if button_id == "submit-button" and input_stock:   

                # If no date selected, use today's date and get most recent data
                if not input_date:
                    today = date.today().strftime('%Y-%m-%d')
                    return self.get_most_recent_data(input_stock, today), current_style

                # Date was selected, try to get data for that specific date
                df = self.get_daily_data(input_stock, input_date)

                if df.empty or df.iloc[0].get('open') is None:  
                    return self.get_most_recent_data(input_stock, input_date), current_style

                row = df.iloc[0].to_dict()

                formatted_data = html.Div([
                    html.Div([
                        html.H3(f"{input_stock.upper()}", style={
                            'color': '#2c3e50',
                            'marginBottom': '5px',
                            'fontSize': '28px',
                            'fontWeight': '600'
                        }),
                        html.P(f"{row.get('from', input_date)}", style={
                            'color': '#7f8c8d',
                            'marginTop': '0',
                            'fontSize': '16px',
                            'marginBottom': '0'
                        }),
                    ], style={'borderBottom': '2px solid #3498db', 'paddingBottom': '15px', 'marginBottom': '20px'}),
                    
                    html.Div([
                        html.Div([
                            html.Div([
                                html.Span("Open", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('open', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#2c3e50',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#ecf0f1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                            html.Div([
                                html.Span("High", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('high', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#27ae60',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#eafaf1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                        ], style={'display': 'flex', 'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Div([
                                html.Span("Low", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('low', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#e74c3c',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#fadbd8',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                            html.Div([
                                html.Span("Close", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                                html.Div(f"${row.get('close', 'N/A')}", style={
                                    'fontSize': '20px',
                                    'fontWeight': '600',
                                    'color': '#2c3e50',
                                    'marginTop': '5px'
                                })
                            ], style={
                                'backgroundColor': '#ecf0f1',
                                'padding': '15px',
                                'borderRadius': '8px',
                                'flex': '1',
                                'margin': '5px'
                            }),
                        ], style={'display': 'flex', 'marginBottom': '10px'}),
                        
                        html.Div([
                            html.Span("Volume", style={'color': '#7f8c8d', 'fontSize': '14px'}),
                            html.Div(f"{row.get('volume', 'N/A'):,}", style={
                                'fontSize': '20px',
                                'fontWeight': '600',
                                'color': '#8e44ad',
                                'marginTop': '5px'
                            })
                        ], style={
                            'backgroundColor': '#f4ecf7',
                            'padding': '15px',
                            'borderRadius': '8px',
                            'margin': '5px'
                        }),
                    ])
                ], style={
                    'backgroundColor': 'white',
                    'padding': '25px',
                    'borderRadius': '10px',
                    'boxShadow': '0 2px 8px rgba(0,0,0,0.1)'
                })
                return formatted_data, current_style

            return html.Div("", id="no-valid-input"), current_style
 
    def layout(self):
        #dashboard layout

        available_tickers = self.fetch_polygon_tickers()
        ticker_options = [{'label': ticker, 'value': ticker} for ticker in available_tickers]
 
        self.app.layout = html.Div([
            # Header container
            html.Div([
                #Header title
                html.H1("📈 Stock Market Dashboard", style={
                    'color': '#2c3e50',
                    'textAlign': 'center',
                    'marginBottom': '10px',
                    'fontSize': '36px',
                    'fontWeight': '700'
                }),
                #Header description
                html.P("Real-time stock data lookup powered by Polygon API", style={
                    'textAlign': 'center',
                    'color': '#7f8c8d',
                    'marginTop': '0',
                    'marginBottom': '0',
                    'fontSize': '16px'
                })
            ], style={
                'backgroundColor': 'white',
                'padding': '30px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                'marginBottom': '30px'
            }),
            
             # Search bar and calendar button container
            html.Div([
                html.Div([
                    dcc.Dropdown(
                        id="input-stock",
                        options=ticker_options,
                        placeholder="Enter stock ticker (e.g., AAPL, VOO, MSFT)",
                        searchable=True,
                        clearable=True,
                        style={
                            'fontSize': '16px',
                            'flex': '1'
                        }
                    ),
                    html.Div([
                        html.Button('Date', 
                            id="calendar-button",
                            style={
                                'backgroundColor': "#60e4b8",
                                'color': 'white',
                                'border': 'none',
                                'borderRadius': '6px',
                                'fontSize': '16px',
                                'cursor': 'pointer',
                                'height': '38px',
                                'width': '50px'
                            }
                        ),
                        # Date picker (hidden by default, positioned absolutely)
                        html.Div([
                            dcc.DatePickerSingle(
                                id="input-date",
                                display_format='YYYY-MM-DD',
                            ),
                        ], id="date-picker-container", style={
                            'display': 'none',
                            'position': 'absolute',
                            'top': '45px',
                            'right': '0',
                            'zIndex': '1000',
                            'backgroundColor': 'white',
                            'padding': '10px',
                            'borderRadius': '8px',
                            'boxShadow': '0 4px 12px rgba(0,0,0,0.15)',
                            'minWidth': '300px'
                        }),
                    ], style={
                        'position': 'relative',
                        'marginLeft': '10px'
                    }),
                ], style={
                    'display': 'flex',
                    'alignItems': 'center',
                    'marginBottom': '10px'
                }),
                
                # Submit button
                html.Button('Get Stock Data', 
                    id="submit-button",
                    style={
                        'backgroundColor': '#60e4b8',
                        'color': 'white',
                        'border': 'none',
                        'padding': '14px 30px',
                        'borderRadius': '6px',
                        'fontSize': '16px',
                        'fontWeight': '600',
                        'cursor': 'pointer',
                        'width': '100%',
                        'marginTop': '15px'
                    }
                ),
            ], style={
                'backgroundColor': 'white',
                'padding': '25px',
                'borderRadius': '10px',
                'boxShadow': '0 2px 8px rgba(0,0,0,0.1)',
                'marginBottom': '30px'
            }),
            
            # Output data container
            html.Div(id="output-data"),
            
        ], style={
            'fontFamily': '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
            'backgroundColor': '#f5f6fa',
            'padding': '40px',
            'minHeight': '100vh',
            'maxWidth': '1000px',
            'margin': '0 auto'
        })


    def run(self):
        self.app.run(debug=True)

def main():

    pipeline = StockMarketPipeline()
    dashboard = Dashboard(pipeline)
    dashboard.run()
   
if __name__ == "__main__":
    main()



