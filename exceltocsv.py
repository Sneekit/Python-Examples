# simple script to convert an excel file to a csv for easy parsing with alternate programs

import pandas as pd
import sys
import os

infile = sys.argv[1]

# get delim from arguments
if len(sys.argv)>2:
        delim = sys.argv[2]
else:
        delim=""

# set ending extension and delimiter based on inputs
endextension=".csv"
if delim == "":
        delim = ","
        endextension=".csv"
if delim == "tab" or delim == "TAB":
        delim = "\t"
        endextension=".tab"

# determine base file names
basename = os.path.basename(infile)
filearray = os.path.splitext(infile)
extension = filearray[1]
extensionlist = ['.xlsx','.xls']

if infile == "":
        print("You must provide a file to convert.")
        sys.exit(1)

if os.path.exists(infile) == False:
        print("The specified file does not exist.")
        sys.exit(1)

if extension not in extensionlist:
        print("You must provide a valid excel file.")
        sys.exit(1)

# read in xlsx file
data_xls = pd.read_excel(infile, sheet_name=None)

# export a csv for every sheet if on python 2.7 and above otherwise single sheet only
sheetnum = 0
try:
        for name,sheet in data_xls.items():
                sheetnum += 1
                outfile = filearray[0]+"_sheet"+str(sheetnum)+endextension
                single_sheet = pd.read_excel(infile, sheet_name=name)
                single_sheet.to_csv(outfile)
except AttributeError:
        data_xls.to_csv(filearray[0]+"_sheet1"+endextension,sep=delim)

print(basename+" exported to csv.")
sys.exit(0)
