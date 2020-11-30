#this is a data scraping discord bot that pulls chat data. It also includes a working blackjack and hangman game, along with user stat tracking.

import discord
import random
import mysql.connector
import math

TOKEN = '*REDACTED*'

bot = discord.Client()
db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='discordbot')
sql = db.cursor()

#scrapes data from every message and uploads it to the chatlog table
def upload_message(message):
	global db
	global sql
	query="INSERT INTO chatlog (authorname,authorid,content,serverid,servername,timestamp,channelid,channelname) VALUES (%s,%s,%s,%s,%s,%s,%s,%s);"
	val=(message.author.name,message.author.id,str(message.content),message.server.id,message.server.name,message.timestamp,message.channel.id,message.channel.name)
	try:
		sql.execute(query,val)
		db.commit()
	except:
		print("MySql error, connection restarting...")
		try:
			db = mysql.connector.connect(user='johnm', password='*REDACTED*',host='127.0.0.1',database='discordbot')
			sql = db.cursor()
		except:
			print("Could not connect to MySql")
		sql.execute(query,val)
		db.commit()

#starts a new blackjack game
def blackjack_reset():
	global card_deck
	global user_hand
	global dealer_hand
	card_deck = []
	user_hand = []
	dealer_hand = []
	for x in range(52):
		card_deck.append(x+1)
	blackjack_draw_card(dealer_hand)
	blackjack_draw_card(user_hand)
	dealer_hand.append(-1)

#Generates a fixed length string with a table of the user's blackjack stats. Mode 1 is individual user, mode 2 is leaderboard.
async def blackjack_get_stats(message,mode):
	if mode == 1:
		query="SELECT win,loss FROM blackjack WHERE userid="+str(message.author.id)+";"
	else:
		query="SELECT win,loss,userid FROM blackjack;"
	sql.execute(query)
	result = sql.fetchall()
	datalist = []
	for x in result:
		datalist.append(list(x))

	if not sql.rowcount:
		return ""
	printstring="```"
	str1 = "UserName"
	str2 = "Wins"
	str3 = "Losses"
	str4 = "Win Percentage"
	printstring+=str1.ljust(20)+str2.ljust(20)+str3.ljust(20)+str4.ljust(20)+"\n"
	for x in range(80):
		printstring+="="
	printstring+="\n"

	for x in datalist:
		win=x[0]
		loss=x[1]
		if loss+win > 0:
			ratio = "{:.2f}".format(100*win/(win+loss))
		else:
			ratio = "00.00"
		x.append(ratio)

	if mode == 2:
		datalist.sort(reverse=True, key=key_sort_3)
		if len(datalist)>10:
			max=10
		else:
			max=len(datalist)
		for x in range(max):
			win=datalist[x][0]
			loss=datalist[x][1]
			user = await bot.get_user_info(datalist[x][2])
			name = user.name
			ratio=datalist[x][3]
			printstring+=name.ljust(20)+str(win).ljust(20)+str(loss).ljust(20)+"%"+ratio.ljust(20)+"\n"
		printstring+="```"
	else:
		win=datalist[0][0]
		loss=datalist[0][1]
		ratio=datalist[0][2]
		printstring+=message.author.name.ljust(20)+str(win).ljust(20)+str(loss).ljust(20)+"%"+ratio.ljust(20)+"```"

	return printstring

#update blackjack stats, mode0 = loss, mode1 = win, mode2 = reset
def blackjack_update_stats(message,mode):
	query="SELECT idblackjack FROM blackjack WHERE userid="+str(message.author.id)+" LIMIT 1;"
	sql.execute(query)
	result = sql.fetchone()
	addrec = False
	if result == None:
		addrec = True
	else:
		addrec = False

	if addrec == True:
		query = "INSERT INTO blackjack (userid,win,loss) VALUES (%s,%s,%s);"
		val = (message.author.id,0,0)
		sql.execute(query,val)
		db.commit()

	query = "UPDATE blackjack SET "
	if mode == 2:
		query += "win=0,loss=0"
	elif mode == 1:
		query +="win=win+1"
	else:
		query +="loss=loss+1"
	query +=" WHERE userid="+str(message.author.id)+";"
	sql.execute(query)
	db.commit()

#get the numeric value of a blackjack hand ( list of cards 1-52 )
def blackjack_hand_value(cardlist):
	handvalue = 0
	acecount = 0
	for card in cardlist:
		if card != -1:
			suit = math.floor((card-1)/13)
			face = 1+card-(suit*13)
			if face <= 10:
				value = face
			elif face < 14:
				value = 10
			if face != 14:
				handvalue+=value
			else:
				acecount+=1

	for card in cardlist:
		if card != -1:
			suit = math.floor((card-1)/13)
			face = 1+card-(suit*13)
			if face == 14:
				if handvalue <= 11-acecount:
					handvalue += 11
				else:
					handvalue += 1
	return(handvalue)

#pulls a card from the global card deck and adds it to the provided hand ( list of numbers 1-52 )
def blackjack_draw_card(cardlist):
	global card_deck
	card = card_deck[random.randint(0,len(card_deck)-1)]
	card_deck.remove(card)
	card_deck.sort()
	cardlist.append(card)

#returns a fixed length formatted string for a users hand ( list of numbers 1-52 )
def blackjack_draw_hand(cardlist):
	str1=""
	str2=""
	str3=""
	str4=""
	str5=""
	for card in cardlist:
		if card != -1:
			if card < 1 or card > 52:
				return ""
			suit = math.floor((card-1)/13)
			suitstr = "♠♥♦♣..."[suit]
			face = 1+card-(suit*13)
			if face <= 10:
				facestr = str(face)
			else:
				facestr = "JQKA"[face-11]

			str1+=" ___  "

			str2+="|"+suitstr+facestr
			if face != 10:
				str2+=" "
			str2+="| "

			str3+="|   | "

			str4+="|"
			if face != 10:
				str4+=" "
			str4+=facestr+suitstr+"| "

			str5+=" ¯¯¯  "
		else:
			str1+=" ___   "
			str2+="|   | "
			str3+="| ? | "
			str4+="|   | "
			str5+=" ¯¯¯  "

	printstr=str1+"\n"+str2+"\n"+str3+"\n"+str4+"\n"+str5+"\n"
	return printstr

#sorts a list ascending based on the third value in the list
def key_sort_3(e):
	return float(e[3])

#sorts a list based on the second value in the list
def key_sort_2(e):
	return e[2]

# formats two input strings to be padded and separated and returns them combined
def help_command(command,description):
	return command.ljust(20)+" - "+description+"\n"

# gives a list of users who have used a specific word and some stats on it
def word_usage(message,substr):
	query="SELECT authorname, COUNT(idchatlog) FROM chatlog WHERE LOWER(content) LIKE '%"+substr+"%' GROUP BY authorname"
	sql.execute(query)
	result_list = []
	result = sql.fetchall()
	for x in result:
		result_list.append(list(x))

	query="SELECT authorname,COUNT(idchatlog) FROM chatlog GROUP BY authorname"
	sql.execute(query)
	result2 = sql.fetchall()

	for x in result2:
		for xx in result_list:
			if x[0] == xx[0]:
				xx.append(x[1])
				ratio = round((xx[1]/xx[2])*100,2)
				ratio = "{:.2f}".format(ratio).zfill(5)
				xx.append(ratio)

	result_list.sort(reverse=True,key=key_sort_3)

	output_string="```"
	str1 = "UserName"
	str2 = "Message Count"
	str3 = substr+" Count"
	str4 = substr+" Percentage"
	output_string+=str1.ljust(20)+str2.ljust(20)+str3.ljust(20)+str4.ljust(20)+"\n"
	for x in range(80):
		output_string+="="
	output_string+="\n"

	for x in result_list:
		str1 = str(x[0]).ljust(20)
		str2 = str(x[2]).ljust(20)
		str3 = str(x[1]).ljust(20)
		str4 = "%"+str(x[3]).ljust(20)
		output_string += str1+str2+str3+str4+"\n"

	output_string+="```"
	return output_string

#when the bot is loaded
@bot.event
async def on_ready():
	print("Sneekbot connected!")
	await bot.change_presence(game=discord.Game(name="Chatting with users"))
	hangman_getword()
	blackjack_reset()

#when a message comes in on the channel
@bot.event
async def on_message(message):
	#filter out unwated bots
	if message.author == bot.user or str(message.author.id) == '398266752829489152':
		return
	else:
		upload_message(message)

	com = message.content.lower()

	#usage command
	elif com.startswith('^usage'):
		pos = com.find(" ")
		if pos == -1 and len(com) > pos+1:
			return
		com3 = com[pos+1:len(com)]
		if len(com3)>13:
			com3=com3[0:13]
		await bot.send_message(message.channel,word_usage(message,com3))
		return
	elif com == "^blackjack reset hard" or com == "bresethard":
		blackjack_update_stats(message,2)
	elif com == "^blackjack hit" or com == "^hit" or com == "bhit":
		global user_hand
		global dealer_hand
		blackjack_draw_card(user_hand)
		printstr = "```\nDealer: "+str(blackjack_hand_value(dealer_hand))+"\n"+blackjack_draw_hand(dealer_hand)
		userhandvalue = blackjack_hand_value(user_hand)
		printstr += blackjack_draw_hand(user_hand)+"\nYour Hand: "+str(userhandvalue)
		if userhandvalue > 21:
			printstr += " - BUST! You Lose!"
			blackjack_update_stats(message,0)
			blackjack_reset()
		printstr += "```"
		await bot.send_message(message.channel,printstr)
	#blackjack stand command
	elif ( com == "^blackjack hold" or com == "^blackjack stand" or com == "^hold" or com == "bhold" ) and int(len(user_hand)) > 0:
		#flip over face-down card
		dealer_hand.remove(-1)
		blackjack_draw_card(dealer_hand)
		#check the user hand value to determine what action to take
		userhandvalue = blackjack_hand_value(user_hand)
		usermessage=""
		dealerstr=""
		dealerace=False
		#hit on soft 17, stand on hard 17
		for x in dealer_hand:
			if x % 13 == 0:
				dealerace=True
		if dealerace == True:
			hitlimit = 18
		else:
			hitlimit = 17
		victory=0
		#keep drawing until the limit is hit, checking the dealer hand value
		while blackjack_hand_value(dealer_hand) < hitlimit:
			blackjack_draw_card(dealer_hand)
		dealerhandvalue = blackjack_hand_value(dealer_hand)
		#the dealer has a higher non-bust hand than the player
		if dealerhandvalue > userhandvalue and dealerhandvalue <= 21:
			usermessage="Dealer Wins!"
		#delaer has the same hand value as the player
		elif dealerhandvalue == userhandvalue:
			dealerblackjack=False
			if len(dealer_hand) == 2 and dealerhandvalue == 21:
				dealerblackjack=True
				dealerstr=" - BLACKJACK!"
			if dealerblackjack == True and len(user_hand) > 2:
				usermessage="Dealer Wins!"
			elif dealerblackjack == False and len(user_hand) == 2 and userhandvalue == 21:
				usermessage="BLACKJACK! You Win!"
				victory=1
			else:
				usermessage="Draw!"
				victory=2
		else:
			usermessage="You Win!"
			victory=1
		printstr = "```\nDealer: "+str(blackjack_hand_value(dealer_hand))
		if dealerhandvalue > 21:
			dealerstr=" - BUST!"
		printstr+=dealerstr
		printstr+="\n"+blackjack_draw_hand(dealer_hand)
		userhandvalue = blackjack_hand_value(user_hand)
		printstr += blackjack_draw_hand(user_hand)+"\nYour Hand: "+str(userhandvalue)+" - "+usermessage+"```"
		await bot.send_message(message.channel,printstr)
		if victory <= 1:
			blackjack_update_stats(message,victory)
		blackjack_reset()
	elif com == "^blackjack" or com == "^blackjack help" or com == "bhelp":
		printstring="```\nBlackJack Help\n"
		for x in range(80):
			printstring+="="
		printstring+="\n"
		printstring+=help_command("^blackjack start","Start a new blackjack game")
		printstring+=help_command("^blackjack hit","Draw a card")
		printstring+=help_command("^blackjack hold","Start Dealer's turn")
		printstring+=help_command("^blackjack stand","Same as hold")
		printstring+=help_command("^blackjack stats","Show your win/loss stats")
		printstring+="```"
		await bot.send_message(message.channel,printstring)
		return
	elif com == "^blackjack start" or com == "bstart":
		if -1 in dealer_hand:
			return
		blackjack_reset()
		printstr = "```\nDealer: "+str(blackjack_hand_value(dealer_hand))+"\n"+blackjack_draw_hand(dealer_hand)+"```"
		await bot.send_message(message.channel,printstr)
	elif com == "^blackjack stats" or com == "bstats" or com == "bstat":
		printstring = await blackjack_get_stats(message,1)
		await bot.send_message(message.channel,printstring)
	elif com == "^blackjack status" or com == "bstatus":
		printstring = "```Dealer Hand:\r"
		printstring += blackjack_draw_hand(dealer_hand)
		printstring += "\r"
		printstring += blackjack_draw_hand(user_hand)
		printstring += "\rYour Hand:```"
		await bot.send_message(message.channel,printstring)
	elif com == "^blackjack leader" or com == "bleader" or com == "blead":
		printstring = await blackjack_get_stats(message,2)
		await bot.send_message(message.channel,printstring)

bot.run(TOKEN)
