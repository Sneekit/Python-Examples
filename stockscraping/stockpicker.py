# program to scan the MySQL database and determine stocks that may be worth day trading with.
# ranks stocks with a score based on consistency
# stock graphs are generated and stored in the local directories
# email notifications go out daily with recommneded stocks

from __future__ import print_function
import argparse

parser = argparse.ArgumentParser(description='Which Stocker. Finds stocks worth day trading.')
parser.add_argument('-k',dest="k",action="store_true",default=False,help="Keep Previous Graphs/Results")
parser.add_argument('-a',dest="a",action="store_true",default=False,help="Send out alerts based on results")
parser.add_argument('-e',dest="e",action="store",type=str,default="",help="Email to send alerts to")
parser.add_argument('-t',dest="t",action="store",type=str,default="",help="Individual Ticker to analyze")
parser.add_argument('-s',dest="s",action="store",type=str,default="",help="Ticker or Letter to start with")
args = parser.parse_args()

print("Loading libraries")

import math
import numpy as np
import pandas as pd
import mysql.connector
import stockutils
import datetime
import matplotlib.pyplot as matplotlib
import matplotlib.dates as mdates
import traceback
import os
from statistics import mean

print("Loading methods")

# generate a pdf graph of the dataframe at the given path
def graph_ticker(data, path, score):
	print("\tGenerating graph")

	# generate a graph with the stock price
	fig = matplotlib.figure(figsize=(12,30))
	fig.patch.set_facecolor('white')

	# generate plot for each unique day of the series
	plotCount = 0
	totalPlots = len(data['day'].unique())
	for x in data['day'].unique():
		plotCount += 1
		plotdata = data.loc[data['day'] == x]
		ax = fig.add_subplot(totalPlots,1,plotCount)
		ax.set_title(str(plotdata['Datetime'][-1]))
		ax.set_ylabel(ticker+" Price ($)")
		ax.xaxis.label.set_visible(False)
		plotdata['OPEN'].plot(ax=ax, color='r', lw=2, label='Price', use_index=True)
		ax.legend()
		ax.yaxis.grid(linestyle=":")
		#ax.xaxis.set_major_formatter(mdates.DateFormatter('%I:%M %p'))

	fig.suptitle(str(data['ticker'][-1])+" - Score: "+str(score), fontsize=16)
	#try:
	matplotlib.subplots_adjust(hspace=.5)
	#matplotlib.tight_layout()
	matplotlib.show()
	fig.savefig(path)
	os.chmod(path, 0o666)
	#os.chown(path, 1001, 1003)
	#except:
		#print("\tFailed to Generate Graph")

	matplotlib.close(fig)
	
# clear all old graphs from the server
def remove_graphs():
	print("Removing old graphs")
	folder = "/stocker/graphs/"
	for the_file in os.listdir(folder):
		file_path = os.path.join(folder, the_file)
		try:
			if os.path.isfile(file_path):
				os.unlink(file_path)
		except Exception as e:
			print("Exception: "+str(e)+"\n"+str(traceback.format_exc()))

# send out notification
def send_notifications():
	print("Sending E-mail notifications")
	import smtplib 
	from email.mime.multipart import MIMEMultipart 
	from email.mime.text import MIMEText 
	from email.mime.base import MIMEBase 
	from email import encoders
	
	emaillist = []
	if args.e != "":
		emaillist.append(args.e)
	else:
		emaillist.append("happyjohndavid@gmail.com")
		emaillist.append("b8steven@gmail.com.com")
		
	query = "SELECT ticker,score FROM stockpick ORDER BY score DESC LIMIT 10;"
	sql.execute(query)
	result = sql.fetchall()
	
	if result == None:
		print("No stockpicks found")
		return
	
	emailBody = "Here are the top 10 stockpickss for day trading:\n\n"
	for res in result:
		emailBody += "Ticker ["+str(res[0])+"]: "+str(res[1])+"\n"
		
	if emailBody != "":
		for email in emaillist:
			print("Sending email to "+email)
			msg = MIMEMultipart()
			fromaddr = "stockstalkeralerts@gmail.com"
			password = "*REDACTED*"
			msg['From'] = fromaddr
			msg['To'] = email
			msg['Subject'] = "Here are the top 10 day trading picks."
			msg.attach(MIMEText(emailBody,'plain'))
			# Attachments are handled here
			#filename = "attachfile.pdf"
			#attachment = open(filename,"rb")
			#p = MIMEBase('application','octet-stream')
			#p.set_payload((attachment.read())
			#encoders.encode_base64(p)
			#p.add_header('Content-Disposition','attachment; filename= %s' % filename)
			#msg.attach(p)
			smtp = smtplib.SMTP('smtp.gmail.com',587)
			smtp.starttls()
			smtp.login(fromaddr,password)
			messagetext = msg.as_string()
			smtp.sendmail(fromaddr,email,messagetext)
			smtp.quit()
					
	print("E-mail notifications sent ("+str(len(emaillist)))
		
# add qualifying ticker to database
def add_stockpick(ticker,score):
	query = "SELECT idstockpick FROM stockpick WHERE ticker='"+str(ticker)+"';"
	sql.execute(query)
	result = sql.fetchone()
	
	if result == None:
		query = "INSERT INTO stockpick(ticker,score) VALUES('"+str(ticker)+"','"+str(score)+"');"
	else:
		query = "UPDATE stockpick SET ticker='"+str(ticker)+"', score='"+str(score)+"' WHERE ticker='"+str(ticker)+"';"
	sql.execute(query)
	db.commit()
	
def clear_stockpicks():
	print("Clearing previous results")
	# remove previous picks
	query = "DELETE FROM stockpick WHERE idstockpick >= 0;"
	sql.execute(query)
	
	# reset auto increment
	query = "ALTER TABLE stockpick AUTO_INCREMENT = 1;"
	sql.execute(query)
	
	# commit to db
	db.commit()
	
if __name__ == '__main__':																				#Start here.
	print("Connecting to database")
	db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='Stock')
	sql = db.cursor()
	
	if args.a == True:
		send_notifications()
		quit

	today = datetime.datetime.combine(datetime.date.today(),datetime.datetime.min.time())
	maxPrice = 10
	validThreshold = 15
	daySpan = 30
	graphSpan = 7
	
	if args.s != "" or args.t != "":																	#Keep graphs if partial run
		args.k = True

	if args.k == False:
		remove_graphs()
		clear_stockpicks()

	if args.t == "":
		print("Loading active stocks from NASDAQ")
		tickerlist=stockutils.get_active_tickers()												#Get all active stock tickers.
		
		if args.s != "":																					#Start with ticker/letter
			startindex = 0
			
			if args.s in tickerlist:																	#Starting ticker chosen
				startindex = tickerlist.index(args.s)
				
			else:
				for ticker in tickerlist:																#If not found above use starting letter
					if ticker.startswith(args.s[0:1]):
						startindex = tickerlist.index(ticker)
						break
						
			tickerlist = tickerlist[startindex:]													#Trim the tickerlist
	else:
		tickerlist=[args.t]
	tickerPad = len(str(len(tickerlist)))
	tickersWeLike = []
	# generate a dataframe with 5 minute data for each of those stocks
	print("Processing Stocks\n")
	y = 0
	finalCSV = pd.DataFrame()																			#Create dataframe for good tickers.
	for ticker in tickerlist:																			#Loop through all active tickers.
		y+=1
		print(str(str(y).zfill(tickerPad))+"/"+str(len(tickerlist))+" Processing ["+str(ticker)+"]")	#Print where we are in the run.
		try:
			try:
				df=stockutils.get_historic(ticker,60)												#Get stock data for 60 day period.
			except KeyboardInterrupt:																	#Quit with CTRL+C
				print("Program Terminated")
				quit()
			except:
				print("\tUnable to retrieve historic data")
				continue
				
			df['costPerShare'] = df['OPEN']
			
			#Date of stock price is index of df, so moving to column.
			df['Datetime'] = df.index

			#print(df)
			try:
				df['Datetime'] = pd.to_datetime(df['Datetime'])									#Ensure there is nothing strange going on with the data.
			except:
				print('Failed to convert to datetime.')

			
			df = df.loc[df['Datetime'] >= today - datetime.timedelta(days=daySpan)]		#Just look at df for our time period.

			meaner = df['costPerShare'].mean()
			if (meaner > maxPrice):																		#If the stock has an average price for a 60 day period greater than what we want then skip it.
				print("\tSkipped! - price above maximum")
				continue
			
			#Dates all spliced out
			df['Datetime'] = df['Datetime'].astype(str)
			df['year'] = df['Datetime'].str.slice(0,4)
			df['month'] = df['Datetime'].str.slice(5,7)
			df['day'] = df['Datetime'].str.slice(8,10)
			df['hour'] = df['Datetime'].str.slice(11,13)
			df['minute'] = df['Datetime'].str.slice(14,16)
			df['hourandmin'] = df['hour'].astype(int) * 60 + df['minute'].astype(int)

			#Initialize our columns.
			df['high'] = 0
			df['low'] = 0
			df['highs'] = 0
			df['lows'] = 0
			df['diff'] = 0
			df['ticker'] = ticker
			df['meanCost'] = meaner
			
			df['Datetime'] = pd.to_datetime(df['Datetime'])

			k = 0				# valid sell points
			b = 0				# invalid sell points
			avgDiff = []
			print("\tDetermining viability...")
			rowCount = len(df['day'].unique())
			for x in df['day'].unique(): 																#Loop through each day for the period.
				da = df.loc[(df['day'] == x) & (df['hourandmin'] > 570)]						#Make sure the high wasn't at the open for the day 570 = 570 minutes, so, 9:30AM, stock market open
				da['high'].loc[da['costPerShare'] == max(da['costPerShare'])] = 1			#Find high for day
				da['low'].loc[da['costPerShare'] == min(da['costPerShare'])] = 1			#find low for day
				damax = da['costPerShare'].loc[da['high'] == 1]
				dalow = da['costPerShare'].loc[da['low'] == 1]

				#Get rid of multiple highs.
				damax = damax.drop_duplicates()
				dalow = dalow.drop_duplicates()
				avgDiff.append(float(damax.values) / float(dalow.values))					#Making sure the difference is worth while enough to care.
				

				da['closetohigh'] = (damax.values - da['costPerShare']) / damax.values	#What percentage is each value from the high
				da['closetolow'] = (da['costPerShare'] - dalow.values) / dalow.values	#What percentage is each value from the low

				da['lows'].loc[da['closetolow'] <= .01] = 1										#If within percentage of low then make a 1			
				da['highs'].loc[da['closetohigh'] <= .01] = 1									#If within percentage of High then make a 1

				range=5
				da['min'] = da['costPerShare'][(da['costPerShare'].shift(range) > da['costPerShare']) & (da['costPerShare'].shift(-range) > da['costPerShare'])]
				da['max'] = da['costPerShare'][(da['costPerShare'].shift(range) < da['costPerShare']) & (da['costPerShare'].shift(-range) < da['costPerShare'])]
				
				da['diff'] = damax.values - da['costPerShare']									#Show dollar amount difference from high of day
				dg = da.loc[(da['lows'] == 1) & (da['hourandmin'] > 570)]					#grab lows for day
				dg = dg.loc[dg['hourandmin'] == min(dg['hourandmin'])]
																	
				dg2 = da.loc[(da['costPerShare'] >= 1.03 * float(dg['costPerShare'].values)) & ((da['hourandmin'] - float(dg['hourandmin'].values)) >= 60)]		#See if there is a high after a low for the day. If 1 exists then we are good for the day.
				
				if (len(dg2)) > 0:																		#If there is a value in dg2 that means something qualifies.
					k+=1
				else:
					b+=1
					
				if b > rowCount-validThreshold:														#Break if we have gone under our minimum number of good days.
					break

			score = k*10
				
			if args.t != "":																				# always graph with a chosen ticker
				graphdata = df.loc[df['Datetime'] >= today - datetime.timedelta(days=graphSpan)]
				graph_ticker(graphdata, "/stocker/graphs/"+str(ticker)+"_"+str(str(score).zfill(3))+".pdf", score)
				graphed = True
			else:
				graphed = False

			if k > validThreshold:																		#If we have a good ticker for the period make a graph.
				finalCSV = pd.concat([finalCSV,df], axis = 0, ignore_index=True)			#Concat df into a big dataframe at end so that we retain data on the ticker.
				tickersWeLike.append(ticker)

				if not graphed:
					graphdata = df.loc[df['Datetime'] >= today - datetime.timedelta(days=graphSpan)]
					graph_ticker(graphdata, "/stocker/graphs/"+str(ticker)+"_"+str(str(score).zfill(3))+".pdf", score)
				print("\tUpdating database")
				add_stockpick(ticker,score)
			else:
				print("\tSkipped! - failed viability")
				
		except Exception as e:
			print("Exception: "+str(e)+"\n"+str(traceback.format_exc()))					#Print exception and stocktrace for said exception.

	finalCSV.to_csv('/stocker/goodStocks/GoodStockResults.csv', index = False)			#Upload to CSV so that we actually have some data for the tickers.
	os.chmod('/stocker/goodStocks/GoodStockResults.csv',0o666)
	os.chown('/stocker/goodStocks/GoodStockResults.csv', 1001, 1003)
	print('We like these tickers:')
	print(tickersWeLike)
