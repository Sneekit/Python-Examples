# Script that pulls a list of tickers from Nasdaq, iterates through them, and pulls stock data from the yahoo finance database.
# Used as a library for other stock scraping utilities

import urllib.request as url
import requests
import pandas as pd
import datetime
from datetime import timedelta
import arrow
import mysql.connector
import matplotlib.pyplot as matplotlib

# get a list of every ticker from Nasdaq hosted text file
def get_active_tickers():
   activetickers = list()
   file = url.urlopen("ftp://ftp.nasdaqtrader.com/SymbolDirectory/nasdaqtraded.txt")
   for ticker in file:
      # convert line to string, split with delim, pull second value
      ticker = str(ticker).split("|",2)[1]
      if ticker != "Symbol" and ticker != "" and "$" not in ticker:
         activetickers.append(ticker)

   return activetickers

# returns historic stock data based on 5 minute intervals and a provided number of days in the past
# ticker - stock ticker to retrieve data for
# days - number of days in the past to go back for data ( max 60 )
def get_historic(ticker, days):
    return get_stockdata(ticker, str(days)+"d", "5m")

# returns live price or live stock info for a specific ticker
# ticker - stock ticker to retrieve data for
# full - 0 for current price, 1 for all current info
def get_live_price(ticker, full):
    df = get_stockdata(ticker, "1d", "1d")
    
    if full == 1:
        return df
    else:
        return df['CLOSE'][-1]

# ticker - stock ticker to retrieve data for
# range - how far back to go for the data
# interval - how often to poll the data
def get_stockdata(ticker, rng, interval):
    url = "https://query1.finance.yahoo.com/v8/finance/chart/"+ticker+"?range="+rng+"&interval="+interval
    result = requests.get(url)
    data = result.json()
    body = data['chart']['result'][0]

    dt = datetime.datetime
    # convert the yahoo finance datetime to pandas manageable datetime
    dt = pd.Series(map(lambda x: arrow.get(x).datetime.replace(tzinfo=None)+timedelta(hours=-4), body['timestamp']), name='Datetime')
    df = pd.DataFrame(body['indicators']['quote'][0], index=dt)
    df = df.loc[:, ('open', 'high', 'low', 'close', 'volume')]
    df.dropna(inplace=True)
    df.columns = ['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOLUME']

    return df
