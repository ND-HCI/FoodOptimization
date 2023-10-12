import csv
from anytree import Node, RenderTree
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

    # Get the food_code
    food_code = row['food_code']
    
    # Get the description
    description = row['description']
    
    # Combine the food_code and the description
    food_code_description = str(food_code) + " " + description

    # Check if this food_code_description has already been added to the parent node
    if food_code_description not in added_categories[parent] and parent != Other:
        # If not, add a new node for this food_code_description under the parent
        Node(food_code_description, parent=parent)

        # And add the food_code_description to the set for this parent node
        added_categories[parent].add(food_code_description)

# Now you can print your tree
for pre, _, node in RenderTree(root):
    print("%s%s" % (pre, node.name))
