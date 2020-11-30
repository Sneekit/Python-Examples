# script to convert raw ticket information into salesforce compatible import file

import os
import pandas
import math
import csv

# method to generate csv from xlsx files
def convert_excel(infile):
	row_count=0

	# import xlsx as data frame
	print("Loading Excel File")
	df = pandas.read_excel(infile, sheet_name=0)

	# create new column for account id
	print("Creating AccountID Column")
	df['AccountID']=df['CustID'].astype(str)

	# convert dsn to account id in new column
	print("Converting Rows")

	for i, row in df.iterrows():
		df.at[i,'CustomNumber'] = calculate_custnum(row)
		df.at[i,'AccountID'] = calculate_acctid(row)
		df.at[i,'CustomType'] = calculate_type(row)
		df.at[i,'Description'] = calculate_description(row)

	print("Dropping columns")

	todrop = [
		'CustType','CallType','Priority','CDuration','CallCount','StopWatch',
		'ClosedTime','Cause','RecvdTime','ModBy','ModDate',
		'ModTime','DTLastMod','ActivType','SLAUrgent','SLAID','QuickCall',
		'CSRating','RatingDesc','RatingSymb','HoldReason','HoldDescription',
		'Product','ChargeTime','Support','Topic','Detail','JiraID','CallState',
		'Rating','RatingRemark','CallID2','CourseName','CourseNum','Instructor',
		'PreReq','CourseLoc','CourseDate','CourseLeng','ConfDate','SentConf','CHKPower',
		'CHKPaper','CHKPath','CHKSelect','CHKToner','ErrCode','ErrDesc','ErrSoln',
		'AssetTag','SubCallType','PrinterSN','Comments','CourseTime','ConnectedTo',
		'Component','Asset_ID','Asset_Desc','Make','Model','Serial_Num','Asset_Scan_Date',
		'OS','OS_Version_String','Purchase_Date','Total_Memory','ARby','PaidProg',
		'ErrorNo','ErrorDescrip','ErrorCause','ErrorLineNo','PcoreFile','Company','ErrorInfo',
		'Examples','CanRecreate','DownSystem','FileName','IndexNum','AuthRcvd','IndexRebld',
		'Xpand','FileCopy','FileName2','FileName3','FreeSpace2','FileSystem2','ReportName',
		'Fax','Shipper','ShipSpeed','AriveDate','DakcsPay','custpay','StingSales','VicSales',
		'FootPrintSales','Upgrade','FollowUp','Conversion','SalesExhibits','SchoolTraining',
		'ContractRcvd','IMSLicense','IMSUSERS','IMSQuery','IMSQUser','Term','TermVersion',
		'BackupSoftware','BackupVersion','LoanTrak','BarcodeScanner','Hardware','IMSDATE',
		'IMSQDATE','TermDate','BackupDate','LoanTrakDate','BarcodeDate','HardwareDAte',
		'Trainer1','Trainer2','Depart1','Return1','Depart2','Return2','Hotelname',
		'HotelAddr','HotelConfNum','HotelPhone','HotelRate','CarRentalName','CarConfNum',
		'CarRate','FaxSent','FaxDate','TapeDate','TapeRead','Tapereadable','Tapetype','UnixVer',
		'InstallDate','WhoInstall','Directory','FaxRcvd','FAXRcvdDate','TapeSend',
		'RevVersion','AdmLayout','COLLCODEFN','TapeDrops','Tapedropconv','Auxcomaker','AUXTAPEDROP',
		'Legal','Comaker','LEGTRANS','LEGTRANSADM','COLLDEBT','COLLDEBTINDEX','Softwareupdate',
		'COLLDEBT1','COLLDEBT1Soft','opsys2k','admdate','LEGTRANSDSP','LEGTRANSDATE','COLLDEBTDSP',
		'COLLDEBTDATE','COLLDEBT1DATE','Legtrans2ndindex','whoreq','Email','CompanyPassword',
		'Other_Request','Error_Number','Line_Number','Prog_Name','Error_Desc','Files_To_Expand',
		'OP_Question','HoursSpent','DTLastMod3','ProjectHours','ProjectType','PatchedPrograms',
		'PatchReason','StingPatch','BeyondPatch','dsxqiPatch','OtherPatch','StatusDescription',
		'RequestedBy','SaleAmount','ConversionAmount','TrainingAmount','DiscountAmount',
		'PaidCommission','SalesmanName','TrainerName','ProgrammingAssigned','AuthSent',
		'MenuOption','ProgramName'
		]
	df.drop(todrop,axis=1,inplace=True)

	print("Renaming Columns")
	rename_columns = {'Status':'Heat Status'}
	df.rename(columns=rename_columns)

	print("Generating Columns")
	df['Status']="HEAT"

	# export to excel file now it has been fixed
	print("Exporting to Excel")
	df.to_excel(outfile, index = False, header=True)

def load_acctid(file):
	tempdict={}
	# convert csv to dataframe
	print("Loading AccountID File")
	df = pandas.read_csv(file)

	print("Generating AccountID Dictionary")
	# iterate through all rows in csv
	for index,row in df.iterrows():
		tempdict[row['Customer number']]=row['Account ID']

	# return the new dictionary
	return tempdict

def calculate_type(r):
	type=str(r['CustomType'])
	if typedict.has_key(type):
		type=typedict[type]

	return type.title()

def calculate_acctid(r):
	dsn=str(r['AccountID'])
	if acctid.has_key(dsn):
		return(acctid[dsn])
	else:
		return("Not Found")

def calculate_custnum(r):
	heatid=int(r['CallID'])
	return "C-"+str(heatid).zfill(6)

def calculate_description(r):
	desc = r['Description']

	if desc == "":
		desc="N/A"

	return desc

def build_typedict():
	d={}
	d['nan']="Custom"
	d['16 - Customs']="Custom"
	d['19 - Dakcsnet']="Dakcsnet"
	d['26 - Client Services']="Client Services"
	d['ADDITIONAL COMPANY']="New Company"
	return d

# build outbound file
outfile="/home/johnm/python/heat/customexport.xlsx"
acctfile=open("/home/johnm/python/heat/AccountID.csv","r")

acctid=load_acctid(acctfile)
acctfile.close()

typedict=build_typedict()

# Main start point, define directory and list files
directory="/home/johnm/python/heat"
convert_excel(directory+"/Heat Call Export Customs2.xlsx")

