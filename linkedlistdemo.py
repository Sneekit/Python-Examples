import linkedlist as ll

mylist = ll.LinkedList()
mylist.addlast("WED")
mylist.addfirst("TUE")
mylist.addfirst("MON")
mylist.addlast("THU")
mylist.addlast("FRI")
mylist.addlast("MON")
mylist.printlist()

print("REMOVE LAST OCCURANCE OF 'MON'")
mylist.removekey("MON",-1)
mylist.printlist()

print("REVERSE THE LIST")
mylist.reverselist()
mylist.printlist()
