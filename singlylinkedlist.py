# this singly linked list contains a tail, which speeds up the addlast method, but breaks the persistence of the data structure
# some methods have been included assuming there is no tail

class Node:
    def __init__(self, data=None):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None
        self.tail = None

def printlist(self):
    node = self.head
    while node is not None:
        print(node.data)
        node = node.next

def addlast(self,data):
    newnode = Node(data)
    self.tail.next = newnode
    self.tail = newnode

def addlastwithouttail(self,data):
    newnode = Node(data)

    # if there is no data in the list, this is the first and the last
    if self.head is None:
        self.head = newnode
        self.tail = newnode
        return

    # iterate through all nodes in linked list to get the last
    last = self.head
    while(last.next):
        last = last.next
    last.next = newnode
    self.tail = newnode

def addfirst(self,data):
    newnode = Node(data)
    newnode.next = self.head
    self.head = newnode

def reverselist(self):
    previoushead = self.head
    previoustail = self.tail

    current = self.head
    while(current.next):
        previousnode = current
        current = current.next
        current.next = previousnode

    self.tail = previoushead
    self.head = previoustail

def removekey(self,removedata):
    # empty list, can't remove data
    if self.head is None:
        return

    # does the first entry match the data to remove?
    if self.head.data == removedata:
        # is there a second entry in the list?
        if self.head.next is not None:
            self.head = self.head.next
        # no second entry, null the list
        else:
            self.head = None
        return

    current = self.head
    prev = current
    while current is not None:
        if current.data == removedata:
            # is there another value after this one?
            if current.next is not None:
                prev.next = current.next
            # if there is not, clear out the next value and update tail.
            else:
                prev.next = None
                self.tail=prev
            
        # on to the next node
        prev = current
        current = current.next
