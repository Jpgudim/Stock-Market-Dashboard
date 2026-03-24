# Stock Market Dashboard

A web dashboard that visualizes real-time stock market data from Polygon API.

## Features
- Can show price and volume for any publicly traded security
- Date selection and error handling

## Technologies
- Python 3.x
- Dash library
- Polygon API
- Libraries: Dash, Pandas, requests

## Installation
1. Clone the repository
```
git clone https://github.com/Jpgudim/Stock-Market-Dashboard.git
cd stock-market-dashboard
```

2. Create virtual environment
```
python -m venv venv
```
Windows
```
source venv\Scripts\activate
```
Mac/Linux
```
source venv/bin/activate
```

3. Install dependencies
```
pip install -r requirements.txt
```

4. Get an API key from Polygon (Now known as Massive)
https://massive.com/

## Usage
Run the dashboard
```
python dash_app.py
```
Then open your browser to http://127.0.0.1:8050/
