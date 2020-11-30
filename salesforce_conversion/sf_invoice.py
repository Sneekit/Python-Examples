# script to take raw data from invoice file export and convert it to salesforce ready import file

import os
import pandas
import math
import csv

# method to generate excel file with acctid xref
def convert_file(infile):
	row_count=0

	# import xlsx as data frame
	print("Loading Invoice File")
	df = pandas.read_csv(infile)

	# make the first column the account id from the xref
	row_count = 0.00
	print("Converting rows")

	# convert ID column to a datatype of string
	df['ID']=df['ID'].astype(str)

	# load acctid for each row based on dsn
	for i, row in df.iterrows():
		# printing slows down processing, disable on larger conversions
		if (math.floor(row_count/1000) == (row_count/1000)):
			print(row_count)

		row_count += 1

		df.at[i,'ID'] = calculate_acctid(row)

	# export to excel file now it has been fixed
	print("Exporting to Excel")
	df.to_excel(outfile, index = False, header=True)

def load_acctid(file):
	tempdict={}
	# convert csv to dataframe
	print("Loading Account ID File")
	df = pandas.read_csv(file, header=None)

	print("Generating Account ID Dictionary")
	# iterate through all rows in csv
	for index,row in df.iterrows():
		tempdict[str(row[0])]=str(row[2])

	# return the new dictionary
	return tempdict

def calculate_acctid(r):
	dsn = str(r['Customer number'])
	if acctid.has_key(dsn):
		return(str(acctid[dsn]))
	else:
		return("Not Found")

# build outbound file
directory="/home/johnm/python/finance"
outfile=directory+"/Quickbooks Invoices.xlsx"
acctidfile=open(directory+"/AccountID.csv","r")

# load custid
acctid=load_acctid(acctidfile)
acctidfile.close()

# Main start point, define directory and list files
convert_file(directory+"/quickbook.invoices.csv")
