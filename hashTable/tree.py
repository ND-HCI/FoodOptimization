class Node:
    def __init__(self, value, parent=None):
        self.value = value
        self.parent = parent
        self.children = []

    def add_child(self, node):
        node.parent = self
        self.children.append(node)

    def find(self, value):
        if self.value == value:
            return self
        for child in self.children:
            found = child.find(value)
            if found:
                return found
        return None
    
    def print_tree(self, indent=0):
        print(' ' * indent, self.value)
        for child in self.children:
            child.print_tree(indent + 2)


# Create root node
root = Node('Food')

# Create Level 1 Nodes
Protein = Node('Protein')
Dairy = Node('Dairy')
Grains = Node('Grains')
Fruits = Node('Fruits')
Vegetables = Node('Vegetables')
Other = Node('Other')
#Add Level 1 Nodes to Tree
root.add_child(Protein)
root.add_child(Dairy)
root.add_child(Grains)
root.add_child(Fruits)
root.add_child(Vegetables)
root.add_child(Other)
#Create Level 2 Nodes
# Create Level 1 Nodes
gchild1 = Node('Protein')
gchild2 = Node('Dairy')
gchild3 = Node('Grains')
gchild4 = Node('Fruits')
gchild5 = Node('Vegetables')
gchild6 = Node('Other')
#Add Level 1 Nodes to Tree
root.add_child(child1)
root.add_child(child2)
root.add_child(child3)
root.add_child(child4)
root.add_child(child5)
root.add_child(child6)

# Add grandchildren
grandchild1 = Node('grandchild1')
grandchild2 = Node('grandchild2')
child1.add_child(grandchild1)
child1.add_child(grandchild2)

# Try to find a node
found = root.find('grandchild1')
if found:
    print('Node found:', found.value)
    if found.parent is not None:
        print('Parent of node:', found.parent.value)
else:
    print('Node not found.')

root.print_tree()
