import pandas as pd
from anytree import Node, RenderTree, findall

def create_food_tree(csv_filename):
    # Read the CSV data into a DataFrame
    df = pd.read_csv(csv_filename)

    # Create a dictionary to store the nodes
    nodes = {}

    # Iterate through the rows of the DataFrame and create nodes
    for index, row in df.iterrows():
        if pd.isna(row['Parent_ID']):
            # If Parent_ID is NaN, create the root node
            nodes[row['ID']] = Node(row['Value'])
        else:
            # Otherwise, create a child node and set its parent
            parent_id = int(row['Parent_ID'])
            nodes[row['ID']] = Node(row['Value'], parent=nodes[parent_id])

    # Return the root of the tree
    return nodes[1]

def label_dataset_with_mapping(user_input, tree_root, test_data):
    # Create a new column called 'mapping'
    test_data['mapping'] = None

    # Define the find_leaf_nodes function within the scope of label_dataset_with_mapping
    def find_leaf_nodes(node, leaf_nodes=None):
        if leaf_nodes is None:
            leaf_nodes = []
        if not node.children:
            leaf_nodes.append(node.name)
        else:
            for child in node.children:
                find_leaf_nodes(child, leaf_nodes)
        return leaf_nodes

    # Convert user inputs to lowercase for case-insensitive comparison
    lower_user_inputs = [input_.lower() for input_ in user_input]

    # Find the node that matches the user input
    matching_nodes = findall(tree_root, filter_=lambda node: node.name.lower() in lower_user_inputs)

    for node in matching_nodes:
        # If the node is a leaf node, map it directly
        if not node.children:
            test_data.loc[test_data['Category'].str.lower() == node.name.lower(), 'mapping'] = node.name
        # If the node is not a leaf, find all its leaf nodes and check if they are in user_input
        else:
            leaf_nodes = find_leaf_nodes(node)
            leaf_found = False
            for leaf in leaf_nodes:
                if leaf.lower() in lower_user_inputs:
                    test_data.loc[test_data['Category'].str.lower() == leaf.lower(), 'mapping'] = leaf
                    leaf_found = True
            # If no leaf node is found in user_input, use the parent node
            if not leaf_found:
                test_data.loc[test_data['Category'].str.lower() == node.name.lower(), 'mapping'] = node.name

    # Filter the DataFrame to keep rows with non-empty 'mapping' column
    test_data = test_data[test_data['mapping'].notnull()]

    return test_data



# # Load the test_data DataFrame (you may need to adapt the file path and read method depending on your file format)
# # test_data = pd.read_csv('../test_data/Test_Optimizer_Data.csv')  
# test_data = pd.read_csv('../merged_walmart_data.csv')  

# # Specify user input
# user_input = ["eggs", "whole milk"]  # Update as needed

# # Create the food tree
# root = create_food_tree('../updated_food_hierarchy.csv')  # Replace with the actual path

# # Print the tree
# for pre, _, node in RenderTree(root):
#     print("%s%s" % (pre, node.name))

# # Label the dataset with mapping according to user input and tree hierarchy
# labeled_data = label_dataset_with_mapping(user_input, root, test_data)

# # Print the result or save it to a new CSV file
# print(labeled_data)
# labeled_data.to_csv('labeled_data.csv', index=False)



