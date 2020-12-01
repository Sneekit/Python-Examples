# demonstrates binary tree and some depth first search traversals
# incorporates the linked list library created in this repository

# original tree structure
#
#          1
#          ^
#       2     3
#       ^     ^
#      4 5   6 7
#      ^     ^
#     8     9 10

import binarytree as bt

tree = bt.BinaryTree()
tree.root = tree.Node(1)
tree.root.left=tree.Node(2,tree.Node(4,tree.Node(8)),tree.Node(5))
tree.root.right=tree.Node(3,tree.Node(6,tree.Node(9),tree.Node(10)),tree.Node(7))

print("====================")
print("Level Order")
print("====================")
tree.LevelOrder(tree.root)
print("")

print("====================")
print("In Order")
print("====================")
tree.InOrder(tree.root)
print("")

print("====================")
print("Pre Order")
print("====================")
tree.PreOrder(tree.root)
print("")

print("====================")
print("Post Order")
print("====================")
tree.PostOrder(tree.root)
print("")
