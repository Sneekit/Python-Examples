# Binary tree library file with some Depth First Search Traversals

import linkedlist as ll

class BinaryTree:
	def __init__(self, node=None):
		self.root=node

	class Node:
		def __init__(self, data=None, left=None, right=None):
			self.data=data
			self.left=left
			self.right=right

	def InOrder(self, node):
		if node is not None:
			self.InOrder(node.left)
			print(node.data)
			self.InOrder(node.right)

	def PreOrder(self, node):
		if node is not None:
			print(node.data)
			self.PreOrder(node.left)
			self.PreOrder(node.right)

	def PostOrder(self, node):
		if node is not None:
			self.PostOrder(node.left)
			self.PostOrder(node.right)
			print(node.data)

	def LevelOrder(self, node):
		count=0
		nodelist = ll.LinkedList()
		nodelist.addlast(node)
		while nodelist.head is not None:
			count+=1
			node = nodelist.head.data
			print(node.data)
			if node.left is not None:
				nodelist.addlast(node.left)
			if node.right is not None:
				nodelist.addlast(node.right)
			nodelist.removekey(node,1)
	
	def AddChildData(self, parent, data, branch):
		newnode = self.Node(data)
		if branch == 0:
			parent.left = newnode
			return newnode
		else:
			parent.right = newnode
			return newnode
