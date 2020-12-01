# this singly linked list contains a tail, which speeds up the addlast method, but breaks the persistence of the data structure
# some methods have been included assuming there is no tail

class LinkedList:
	def __init__(self):
		self.head = None
		self.tail = None

	class Node:
		def __init__(self, data=None):
			self.data = data
			self.next = None

	def printlist(self):
		node = self.head
		while node is not None:
			print(node.data)
			node = node.next

	def addlast(self,data):
		newnode = self.Node(data)

		if self.head is None:
			self.head = newnode
		elif self.head.next is None:
			self.head.next = newnode

		if self.tail is None:
			self.tail = newnode
		else:
			self.tail.next = newnode
			self.tail = newnode

	def addlastwithouttail(self,data):
		newnode = self.Node(data)

		# if there is no data in the list, this is the first and the last
		if self.head is None:
			self.head = newnode
			return

		# iterate through all nodes in linked list to get the last
		last = self.head
		while(last.next):
			last = last.next
		last.next = newnode

	def addfirst(self,data):
		newnode = self.Node(data)

		if self.tail is None:
			self.tail = newnode

		if self.head is None:
			self.head = newnode
		else:
			newnode.next = self.head
			self.head = newnode

	def reverselist(self):
		previoushead = self.head
		previoustail = self.tail

		current = self.head
		nextnode = self.head
		previousnode = None

		while current is not None:
			nextnode = current.next
			current.next = previousnode
			previousnode = current
			current = nextnode

		self.tail = previoushead
		self.head = previoustail

	# removedata is the key to be removed
	# occurance is the nth occurance you want to remove, -1 = last
	def removekey(self,removedata,occurance):
		# empty list, can't remove data
		if self.head is None:
			return

		current = self.head
		prev = current
		count = 0
		remove = None
		while current is not None:
			if current.data == removedata:
				remove = current
				count +=1
				if occurance == count:
					break

			# do not update previous node if this is the last one in the list
			if current == self.tail:
				break

			# store previous item in list and iterate the current
			prev = current
			current = current.next

		# did we find one to remove?
		if remove is not None:
			# is this the tail?
			if remove == self.tail:
				# last entry? strip the list entirely
				if remove == self.head:
					remove = None
					self.head = None
					self.tail = None
				else:
					prev.next = None
					self.tail = prev
					current=None
			# is this the head?
			elif remove == self.head:
				# is there more than one item in list?
				if self.head.next is not None:
					self.head = self.head.next
				# there is only one item in the list
				else:
					self.head = None
					self.tail = None
			else:
				prev.next = current.next
