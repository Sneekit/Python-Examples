# python script to rebuild the MySQL database data with ticker information based on a 5 minute interval.
# uses the included stockutils

import requests
import stockutils
import pandas as pd
import datetime
from datetime import timedelta
import arrow
import mysql.connector
import os
import math

# mysql connection
db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='Stock')
sql = db.cursor()

today = datetime.date.today()

def rebuild_stock(ticker,tickerid):
   df = stockutils.get_historic(ticker,60)
   print("Processing Ticker: ",ticker)
   rowcount=0

   for row in df.iterrows():
      rowcount=rowcount+1
      if ((rowcount/100)==math.floor(rowcount/100)):
         print (str(rowcount)+" / "+str(len(df.index)))
      # get the last price scraped today
      sql_date = row[0].strftime('%Y-%m-%d %H:%M:%S')
      query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND datetime='"+sql_date+"' ORDER BY datetime DESC LIMIT 1"
      sql.execute(query)
      result = sql.fetchone()

      # check to see if there is a stock today
      if result == None:
         # insert new record into stock data, testdata has a tickerID of 9999
         query = "INSERT INTO stocks (ticker,costPerShare,datetime,tickerID) VALUES (%s,%s,%s,%s);"
         price = (float)(row[1][1])
         val = (ticker,price,sql_date,tickerid)
         sql.execute(query,val)
         db.commit()
      # skip if there is a stock today and the previous price is the same as the current

   # complete!
   print (str(rowcount)+" / "+str(len(df.index)))

# find all stocks
query="SELECT ticker,idtickerlist FROM tickerlist;"
sql.execute(query)
result = sql.fetchall()
print (result)
# check if there are results, database error if there are no results
if result == None:
   print("Error obtaining ticker list from server.")
   exit
for x in result:
   rebuild_stock(x[0],x[1])
