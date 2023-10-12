import csv
from anytree import Node, RenderTree, PreOrderIter
import pandas as pd

def create_food_tree(schema_file, food_file, survey_file, wweia_file):

    # Create root node
    #This is Level 1
    root = Node('Food')

    # Create Level 1 Nodes and attach to root
    Proteins = Node('Proteins', parent=root)
    Dairy = Node('Dairy', parent=root)
    Grains = Node('Grains', parent=root)
    Fruits = Node('Fruits', parent=root)
    Vegetables = Node('Vegetables', parent=root)
    Other = Node('Other', parent=root)

    # Create a dictionary to map nodes' names to nodes
    name_to_node = {
        'Proteins': Proteins,
        'Dairy': Dairy,
        'Grains': Grains,
        'Fruits': Fruits,
        'Vegetables': Vegetables,
        'Other': Other
    }

    # Create a dictionary to map IDs to nodes
    id_to_node = {}

    # Read the FDC Schema file
    with open(schema_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header

        for row in reader:
            id_description = row[2] 
            parent_id = int(id_description.split()[0])

            if 20 <= parent_id <= 44:
                parent = Proteins
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

            node = Node(id_description, parent=parent)
            name_to_node[id_description] = node
            id_to_node[parent_id] = node

    # Load data from the CSV files into pandas data frames
    food = pd.read_csv(food_file)
    survey = pd.read_csv(survey_file)
    wweia = pd.read_csv(wweia_file)

    # Merge the data frames on the 'fdc_id' column
    merged = pd.merge(food, survey[['fdc_id', 'food_code', 'wweia_category_number']], on='fdc_id')
    merged = pd.merge(merged, wweia[['wweia_food_category', 'wweia_food_category_description']], left_on='wweia_category_number', right_on='wweia_food_category')
    merged['short_description'] = merged['description'].str.split(',').str[0]
    merged = merged[['fdc_id', 'description', 'short_description', 'food_code', 'wweia_food_category', 'wweia_food_category_description']]

    # Create a new set for each node to track the wweia_food_category_description values that have been added as children
    added_categories = {node: set() for node in name_to_node.values()}

    # Iterate over the rows in the DataFrame
    for index, row in merged.iterrows():
        parent_id = int(str(row['food_code'])[:2])
        parent = id_to_node.get(parent_id, Other) 
        short_description = row['short_description']

        if short_description not in added_categories[parent] and parent != Other:
            new_node = Node(short_description, parent=parent)
            name_to_node[short_description] = new_node
            added_categories[parent].add(short_description)

    # Return the root of the tree
    return root, name_to_node


def get_level2_descriptions(root, name_to_node, descriptions):
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

    # Initialize an empty list to hold the Level2 descriptions
    Level2_descriptions = []

    # For each description, find its parent and then add all children of that parent to Level2_descriptions
    for description in descriptions:
        parent_name = child_to_parent.get(description)
        if parent_name:  # Only proceed if the description has a parent in the tree
            parent_node = name_to_node[parent_name]
            Level2_descriptions.extend(get_child_descriptions(parent_node))

    return Level2_descriptions

def get_grandparent_level_descriptions(root, name_to_node, descriptions):
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

    # Initialize an empty list to hold the grandparent-level descriptions
    grandparent_level_descriptions = []

    # For each description, find its parent, then its grandparent, and then add all children 
    # of the parent of that grandparent (i.e., all siblings of the parent and all their children) 
    # to grandparent_level_descriptions
    for description in descriptions:
        parent_name = child_to_parent.get(description)
        if parent_name:  # Only proceed if the description has a parent in the tree
            grandparent_name = child_to_parent.get(parent_name)
            if grandparent_name:  # Only proceed if the parent has a parent in the tree
                grandparent_node = name_to_node[grandparent_name]
                for child in grandparent_node.children:
                    grandparent_level_descriptions.extend(get_child_descriptions(child))

    return grandparent_level_descriptions

def clean_string(s):
    return s.replace('‚Äò', "'").replace('‚Äô', "'")

# def get_parent_nodes(name_to_node, descriptions):
#     parent_nodes = []
#     for description in descriptions:
#         description = clean_string(description)
#         node = name_to_node.get(description)
#         if node and node.parent:  # Only proceed if the node exists in the tree and has a parent
#             parent_nodes.append(node.parent.name)
#     return parent_nodes

def get_parent_nodes(name_to_node, descriptions):
    parent_nodes = []
    for description in descriptions:
        node = name_to_node.get(description)
        if node and node.parent:  # Only proceed if the node exists in the tree and has a parent
            parent_nodes.append(node.parent.name)
    return parent_nodes

def get_grandparent_nodes(name_to_node, descriptions):
    grandparent_nodes = []
    for description in descriptions:
        node = name_to_node.get(description)
        if node and node.parent and node.parent.parent:  # Only proceed if the node exists in the tree and has a parent and grandparent
            grandparent_nodes.append(node.parent.parent.name)
    return grandparent_nodes

def tree_to_csv(root, csv_filename):
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['short_description', 'Parent', 'Grandparent']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for node in PreOrderIter(root):
            if node.is_leaf:  # Check if the node is a leaf node (lowest level node)
                if node.parent is not None:  # Check if the node has a parent
                    grandparent = node.parent.parent.name if node.parent.parent is not None else ''
                    writer.writerow({'short_description': node.name, 'Parent': node.parent.name, 'Grandparent': grandparent})

def test():

    root, name_to_node = create_food_tree(
        schema_file='../schema.csv',
        food_file='../food.csv',
        survey_file='../survey_fndds_food.csv',
        wweia_file='../wweia_food_category.csv'
    )

    # Print the tree
    for pre, _, node in RenderTree(root):
        print("%s%s" % (pre, node.name))

    # Load database
    db = pd.read_csv('../database_fullgrocery_testfile.csv')

    # Create new columns
    db['Parent'] = ''
    db['Grandparent'] = ''

    rows_to_remove = []

    for i, row in db.iterrows():
        keyword = str(row['Keyword']).strip()

        node = name_to_node.get(keyword)

        if node is None:
            print(f"Keyword '{keyword}' not found in the tree.")
            rows_to_remove.append(i)
            continue

        # Get parent node, if it exists
        parent = node.parent
        if parent is not None:
            db.at[i, 'Parent'] = parent.name

            # Get grandparent node, if it exists
            grandparent = parent.parent
            if grandparent is not None:
                db.at[i, 'Grandparent'] = grandparent.name

    # Remove the rows where keyword was not found in the tree
    db = db.drop(rows_to_remove)

    # Save the updated dataframe to a new CSV file
    db.to_csv('../database_fullgrocery_with_parents.csv', index=False)

        # Usage:
    with open('tree2.csv', 'w', newline='') as csvfile:
        fieldnames = ['Level1', 'Level2', 'Level3', 'Level4']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        tree_to_csv(root, writer)


if __name__ == '__main__':
    root, name_to_node = create_food_tree(
        schema_file='../schema.csv',
        food_file='../food.csv',
        survey_file='../survey_fndds_food.csv',
        wweia_file='../wweia_food_category.csv'
    )
    tree_to_csv(root, 'tree2.csv')