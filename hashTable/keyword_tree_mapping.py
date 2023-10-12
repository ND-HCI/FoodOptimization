import csv
from anytree import Node, RenderTree, PreOrderIter
import pandas as pd

# Create root node
root = Node('Food')

# Create Level 1 Nodes and attach to root
Protein = Node('Protein', parent=root)
Dairy = Node('Dairy', parent=root)
Grains = Node('Grains', parent=root)
Fruits = Node('Fruits', parent=root)
Vegetables = Node('Vegetables', parent=root)
Other = Node('Other', parent=root)

# Create a dictionary to map nodes' names to nodes
name_to_node = {
    'Protein': Protein,
    'Dairy': Dairy,
    'Grains': Grains,
    'Fruits': Fruits,
    'Vegetables': Vegetables,
    'Other': Other
}

# Create a dictionary to map IDs to nodes
id_to_node = {}

# Read the FDC Schema file
with open('schema.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header

    # Add child node to respective parent node for each ID in schema
    for row in reader:
        id_description = row[2]  # The combined ID and description
        parent_id = int(id_description.split()[0])  # Assuming the parent's ID is the first word in the id_description

        # Determine the parent node for each id range
        if 20 <= parent_id <= 44:
            parent = Protein
        elif 11 <= parent_id <= 14:
            parent = Dairy
        elif 50 <= parent_id <= 59:
            parent = Grains
        elif 61 <= parent_id <= 67:
            parent = Fruits
        elif 71 <= parent_id <= 78:
            parent = Vegetables
        else:
            parent = Other

        # Create a new node for this row and attach it to the determined parent node
        node = Node(id_description, parent=parent)
        # Add the new node to the name_to_node dictionary
        name_to_node[id_description] = node
        # Add the new node to the id_to_node dictionary
        id_to_node[parent_id] = node

# Load data from the two CSV files into pandas data frames
food = pd.read_csv('../FNDDS_Code_Data/food.csv')
survey = pd.read_csv('../FNDDS_Code_Data/survey_fndds_food.csv')
wweia = pd.read_csv('../FNDDS_Code_Data/wweia_food_category.csv')

# Merge the data frames on the 'fdc_id' column
merged = pd.merge(food, survey[['fdc_id', 'food_code', 'wweia_category_number']], on='fdc_id')
merged = pd.merge(merged, wweia[['wweia_food_category', 'wweia_food_category_description']], left_on='wweia_category_number', right_on='wweia_food_category')
merged['short_description'] = merged['description'].str.split(',').str[0]

# Keep only the desired columns
merged = merged[['fdc_id', 'description', 'short_description', 'food_code', 'wweia_food_category', 'wweia_food_category_description']]

# Create a new set for each node to track the wweia_food_category_description values that have been added as children
added_categories = {node: set() for node in name_to_node.values()}

# Iterate over the rows in the DataFrame
for index, row in merged.iterrows():
    # Get the parent ID
    parent_id = int(str(row['food_code'])[:2])  # Assuming the parent's ID are the first two digits in the food_code

    # Define the parent node using the id_to_node dictionary
    parent = id_to_node.get(parent_id, Other)  # If parent_id is not in id_to_node, use 'Other' as the default parent

    # Get the short_description
    short_description = row['short_description']

    # Check if this short_description has already been added to the parent node
    if short_description not in added_categories[parent] and parent != Other:
        # If not, add a new node for this short_description under the parent
        Node(short_description, parent=parent)

        # And add the short_description to the set for this parent node
        added_categories[parent].add(short_description)

# Now you can print your tree
for pre, _, node in RenderTree(root):
    print("%s%s" % (pre, node.name))

def get_child_descriptions(node):
    """Returns a list of the names of all children of a node."""
    return [child.name for child in node.children]

def get_parents_mapping(node):
    """Builds a dictionary that maps each node to its parent."""
    return {child.name: node.name for child in node.children}

# Create an empty dictionary for child-to-parent mappings
child_to_parent = {}

# Fill the dictionary with mappings for all nodes in the tree
for node in PreOrderIter(root):
    child_to_parent.update(get_parents_mapping(node))

# List of descriptions
descriptions = ["Cheese", "Beef"]

# Initialize an empty list to hold the Level2 descriptions
Level2_descriptions = []

# For each description, find its parent and then add all children of that parent to Level2_descriptions
for description in descriptions:
    parent_name = child_to_parent.get(description)
    if parent_name:  # Only proceed if the description has a parent in the tree
        parent_node = name_to_node[parent_name]
        Level2_descriptions.extend(get_child_descriptions(parent_node))

# Print the Level2 descriptions
print(Level2_descriptions)

