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
    # Create new columns for 'mapping' and 'User Input'
    test_data['mapping'] = None
    test_data['User_Input'] = None

    def find_leaf_nodes(node, leaf_nodes=None):
        if leaf_nodes is None:
            leaf_nodes = []
        if not node.children:
            leaf_nodes.append(node.name)
        else:
            for child in node.children:
                find_leaf_nodes(child, leaf_nodes)
        return leaf_nodes

    lower_user_inputs = [input_.lower() for input_ in user_input]

    for node in findall(tree_root, filter_=lambda node: node.name.lower() in lower_user_inputs):
        leaf_nodes = find_leaf_nodes(node)
        leaf_found = False

        for leaf in leaf_nodes:
            if leaf.lower() in lower_user_inputs:
                test_data.loc[test_data['Category'].str.lower() == leaf.lower(), 'mapping'] = leaf
                # Assign the user input that corresponds to the leaf node
                test_data.loc[test_data['Category'].str.lower() == leaf.lower(), 'User_Input'] = [input_ for input_ in user_input if input_.lower() == leaf.lower()][0]
                leaf_found = True

        # If no leaf node is found in user_input, use the parent node
        if not leaf_found:
            test_data.loc[test_data['Category'].str.lower() == node.name.lower(), 'mapping'] = node.name
            # Assign the user input that corresponds to the parent node
            test_data.loc[test_data['Category'].str.lower() == node.name.lower(), 'User_Input'] = [input_ for input_ in user_input if input_.lower() == node.name.lower()][0]

    # Optionally, filter the DataFrame to keep rows with non-empty 'mapping' column
    # test_data = test_data[test_data['mapping'].notnull()]

    return test_data

def label_parent_nodes(user_input, tree_root, test_data, max_levels=4):
    def get_leaf_nodes(node):
        return [leaf.name for leaf in findall(node, filter_=lambda n: not n.children)]

    def map_dataset(data, leaf_nodes, user_input_label):
        categories = [leaf.lower() for leaf in leaf_nodes]
        filtered_data = data[data['Category'].str.lower().isin(categories)]
        filtered_data['User_Input'] = user_input_label  # Add a column with the original user input
        return filtered_data

    def get_parent_nodes(node, level):
        nodes = []
        current_node = node
        while current_node.parent and level > 0:
            nodes.append(current_node.parent)
            current_node = current_node.parent
            level -= 1
        return nodes

    # Keep the original user inputs for adding to the datasets
    original_user_inputs = user_input
    lower_user_inputs = [input_.lower() for input_ in user_input]

    levels_info = {input_.lower(): count_levels_to_root_excluding_node_and_root(findall(tree_root, filter_=lambda node: node.name.lower() == input_.lower())[0]) for input_ in user_input}
    datasets = {f'dataset_parent{level}': pd.DataFrame() for level in range(3, max_levels + 3)}

    for level in range(3, max_levels + 3):
        level_datasets = []
        for original_input, lower_input in zip(original_user_inputs, lower_user_inputs):
            steps_up = min(levels_info[lower_input], level - 2)
            node = findall(tree_root, filter_=lambda node: node.name.lower() == lower_input)[0]
            parent_nodes = get_parent_nodes(node, steps_up)
            leaf_nodes = [leaf for parent in parent_nodes for leaf in get_leaf_nodes(parent)]
            level_datasets.append(map_dataset(test_data, leaf_nodes, original_input))

        datasets[f'dataset_parent{level}'] = pd.concat(level_datasets).drop_duplicates()

    return datasets


def count_levels_to_root_excluding_node_and_root(node):
    count = 0
    current_node = node.parent  # Start from the parent of the user input node
    while current_node is not None and current_node.parent is not None:  # Stop before the root node
        count += 1
        current_node = current_node.parent
    return count

# root = create_food_tree('../updated_food_hierarchy.csv')
# user_input = ['Chicken Breast', 'Bread']
# test_data = pd.read_csv("../merged_walmart_data_with_images.csv")
# datasets = label_parent_nodes(user_input, root, test_data)

# # Collect level counts for each user input
# levels_count = {}

# for input_ in user_input:
#     lower_input = input_.lower()
#     matching_nodes = findall(root, filter_=lambda node: node.name.lower() == lower_input)
#     if matching_nodes:
#         node = matching_nodes[0]
#         levels_count[input_] = count_levels_to_root_excluding_node_and_root(node)

# # Print level counts for each input
# for input_, count in levels_count.items():
#     print(f"Number of levels from '{input_}' to root, excluding both the input node and root: {count}")

# for key, dataset in datasets.items():
#     print(f"Dataset {key} (Shape: {dataset.shape}):")

# for key, dataset in datasets.items():
#     file_name = f'{key}.csv'
#     dataset.to_csv(file_name, index=False)
#     print(f"{key} saved to {file_name} (Shape: {dataset.shape})")


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



