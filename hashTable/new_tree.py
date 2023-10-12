import csv
from anytree import Node, RenderTree
import json
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

#Level 2 Nodes: 
#Using the Schema located here to map IDs to the parent
# Create a dictionary to map ID ranges to parent nodes
id_to_parent = {}
for i in range(20, 45):
    id_to_parent[i] = Protein
for i in range(11, 15):
    id_to_parent[i] = Dairy
for i in range(50, 60):
    id_to_parent[i] = Grains
for i in range(61, 68):
    id_to_parent[i] = Fruits
for i in range(71, 79):
    id_to_parent[i] = Vegetables

# Read the FDC Schema file
with open('schema.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)  # Skip the header

    #Add Child node to respective parent node for each ID in schema
    for row in reader:
        id = int(row[0])
        description = row[2]  # The combined ID and description
        parent = id_to_parent.get(id, Other)  # If the ID is not in the dictionary, set the parent to Other
        # Create a new node for this row and attach it to the determined parent node
        Node(description, parent=parent)

#Level 3 & 4: 

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

# # Save the merged dataframe to a new CSV file
# merged.to_csv('mergedFNDDS.csv', index=False)

# # Loop over rows of the merged DataFrame
# for index, row in merged.iterrows():
#     food_code = str(row['food_code'])
#     food_code_first_two_digits = food_code[:2]
#     category = row['wweia_food_category_description']

#     # Get the parent for this row from the code_to_parent dictionary
#     parent = code_to_parent.get(food_code_first_two_digits, Other)
# Display the tree
for pre, _, node in RenderTree(root):
    print("%s%s" % (pre, node.name))
