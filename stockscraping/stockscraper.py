# this uses the IEX finance API to scrape stock data every 5 minutes
# also connects to a MySQL database and updates data needed for predictions.

from iexfinance.stocks import Stock
import mysql.connector
import datetime

# mysql connection
db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='Stock')
sql = db.cursor()


# get stock prices from iex finance and upload results to database
def update_stock(ticker,tickerid):
	stock = Stock(ticker)
	price = stock.get_price()

	# get time for processing info
	date_today = datetime.datetime.today()
	time = int((date_today - date_today.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds())
	date = (date_today - datetime.datetime(1899,12,30)).days;

	# get the last price scraped today
	query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND date="+str(date)+" ORDER BY date DESC LIMIT 1"
	sql.execute(query)
	result = sql.fetchone()

	# check to see if there is a stock today
	if result != None:
		# skip if there is a stock today and the previous price is the same as the current
		if result[0] == price:
			return

	# insert new record into stock data, testdata has a tickerID of 9999
	query = "INSERT INTO stocks (ticker,costPerShare,time,date,tickerID) VALUES (%s,%s,%s,%s,%s);"
	val = (ticker,price,time,date,tickerid)
	sql.execute(query,val)
	db.commit()

	# grab the high for the day
	query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND date="+str(date)+" ORDER BY costPerShare DESC LIMIT 1"
	sql.execute(query)
	result = sql.fetchone()

	# update the high for the day
	query = "UPDATE stocks SET high=1 WHERE ticker='"+ticker+"' AND date="+str(date)+" AND costPerShare="+str(result[0])+";"
	sql.execute(query)
	db.commit()

	query = "UPDATE stocks SET high=0 WHERE ticker='"+ticker+"' AND date="+str(date)+" AND costPerShare!="+str(result[0])+";"
	sql.execute(query)
	db.commit()

	# grab the low for the day
	query = "SELECT costPerShare FROM stocks WHERE ticker='"+ticker+"' AND date="+str(date)+" ORDER BY costPerShare ASC LIMIT 1"
	sql.execute(query)
	result = sql.fetchone()

	# update the low for the day
	query = "UPDATE stocks SET low=1 WHERE ticker='"+ticker+"' AND date="+str(date)+" AND costPerShare="+str(result[0])+";"
	sql.execute(query)
	db.commit()

	query = "UPDATE stocks SET low=0 WHERE ticker='"+ticker+"' AND date="+str(date)+" AND costPerShare!="+str(result[0])+";"
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
