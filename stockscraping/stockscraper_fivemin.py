# uses the included stockutils to pull stock data, updates MySQL database with relevant data.

import stockutils as utils
import mysql.connector
import datetime
from datetime import timedelta

# mysql connection
db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='Stock')
sql = db.cursor()


# get stock prices from iex finance and upload results to database
def update_stock(ticker,tickerid):
   data = utils.get_live_price(ticker,0)
   price = float(data)
   #print (ticker," Price: ",price)

   # get time for processing info
   date_today = datetime.datetime.today()+timedelta(hours=2)
   today = date_today.strftime('%Y-%m-%d')
   date = date_today.strftime('%Y-%m-%d %H:%M:%S')

   # get the last price scraped today
   query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' ORDER BY datetime DESC LIMIT 1"
   sql.execute(query)
   result = sql.fetchone()

   # check to see if there is a stock today
   if result != None:
      # skip if there is a stock today and the previous price is the same as the current
      if result[0] == price:
         return

   # insert new record into stock data, testdata has a tickerID of 9999
   query = "INSERT INTO stocks (ticker,costPerShare,datetime,tickerID) VALUES (%s,%s,%s,%s);"
   val = (ticker,price,date,tickerid)
   sql.execute(query,val)
   db.commit()

   # grab the high for the day
   query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' ORDER BY costPerShare DESC LIMIT 1"
   sql.execute(query)
   result = sql.fetchone()

   # update the high for the day
   query = "UPDATE stocks SET high=1 WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' AND costPerShare="+str(result[0])+";"
   sql.execute(query)
   db.commit()

   query = "UPDATE stocks SET high=0 WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' AND costPerShare!="+str(result[0])+";"
   sql.execute(query)
   db.commit()

   # grab the low for the day
   query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' ORDER BY costPerShare ASC LIMIT 1"
   sql.execute(query)
   result = sql.fetchone()

   # update the low for the day
   query = "UPDATE stocks SET low=1 WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' AND costPerShare="+str(result[0])+";"
   sql.execute(query)
   db.commit()

   query = "UPDATE stocks SET low=0 WHERE ticker='"+ticker+"' AND DATE(datetime)='"+str(today)+"' AND costPerShare!="+str(result[0])+";"
   sql.execute(query)
   db.commit()

# find all stocks
query="SELECT ticker,idtickerlist FROM tickerlist;"
sql.execute(query)
result = sql.fetchall()
# check if there are results, database error if there are no results
if result == None:
   print("Line 68: Error collecting ticker list from server.")
   exit
for x in result:
   update_stock(x[0],x[1])
