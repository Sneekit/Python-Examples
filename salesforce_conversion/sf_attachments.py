# script to convert raw attachment information into salesforce compatible import file

import os
import pandas
import math

def add_field(value,use_delim):
	outfile.write('"')
	outfile.write(value.encode('utf8'))
	outfile.write('"')
	if use_delim:
		outfile.write(delim)

# method to generate csv from xlsx files
def generate_csv(infile):
	# reset row count
	row_count = 0
	ex_count = 0
	att_cnt = 0
	not_cnt = 0

	# import xlsx as data frame
	print("Importing excel file")
	df = pandas.read_excel(infile,sheet_name=0)

	print("Processing rows")
	for index,row in df.iterrows():

		row_count += 1

		# skip header
		if row_count == 1:
			continue

		# skip unrelated attachments
		if row['GCode'] != "AT":
			continue

		heatid=row['GName']
		custid=calculate_custid(row)

		# make an array of strings based on newlines
		lines = row['GDetail'].splitlines()

		line_start=0
		for line in lines:
			line_start += 1
			if line.startswith("NumAttachments"):
				break

		line_start = line_start-1

		# calculate number of attachments
		pos = str(lines[line_start]).find("=")
		numattach = int(str(lines[line_start])[pos+1:])

		att_cnt=0
		# get each attachment
		for x in range(numattach):
			att_cnt += 1
			if att_cnt == 1:
				continue
			# get string of this attachment
			try:
				attachment=lines[line_start+3+x]
			except:
				print(lines)
				ex_count = ex_count+1
				print(ex_count)
				break

			# find attachment name and full path
			pos = attachment.find("|")
			name_str = "Attachment"+str(x+1)+"="
			attachment_name = attachment[len(name_str):pos]
			attachment_path = attachment[pos+1:]

			# file name
			pos = attachment_path.rfind("\\")
			file_name = attachment_path[pos+1:]

			# find relative path
			pos = attachment_path.lower().find("bendata")
			if pos <= 0:
				attachment_path = "Unknown"
			else:
				attachment_path = attachment_path[pos+8:]

			if custid != "Not Found":
				att_cnt += 1
				add_field(heatid,True)
				add_field(custid,True)
				add_field(attachment_name,True)
				add_field(attachment_path,True)
				add_field('https://dakcs-heat-archive.s3.us-west-2.amazonaws.com',True)
				add_field(file_name,False)
				outfile.write("\n")
			else:
				not_cnt += 1

	print("Export Complete")
	print("Exceptions: "+str(ex_count))
	print("Attachments: "+str(att_cnt))
	print("No Custid: "+str(not_cnt))

def calculate_custid(r):
	id = "C-"+str(r['GName'])[2:]
	if custid.has_key(id):
		return(custid[id])
	else:
		return("Not Found")

def load_custid(file):
	tempdict={}
	# convert csv to dataframe
	print("Loading CustomID File")
	df = pandas.read_csv(file)

	print("Generating CustomID Dictionary")
	# iterate through all rows in csv
	for index,row in df.iterrows():
		tempdict[row['Custom Number']]=row['Custom Programming: ID']

	# return the new dictionary
	print(tempdict)
	return tempdict

# build outbound file
delim=","
directory="/home/johnm/python/heat"
outfile=open("/home/johnm/python/heat/attachexport3.csv","w+")
outfile.write("heatid,custom id,attachment name,link,URL,FileName\n")
custfile=open(directory+"/Results and ID.csv","r")

# load custid
custid=load_custid(custfile)
custfile.close()

# Main start point, define directory and list files
generate_csv("/home/johnm/python/heat/Heat Attachments.xlsx")

# close the file
outfile.close()
