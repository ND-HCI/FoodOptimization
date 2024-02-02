import json
import csv
from collections import Counter
from sklearn.preprocessing import StandardScaler
from Optimizer2 import NutOptimizer
import pandas as pd
from python_functions.get_food_code import get_food_codes, lookup_food_codes, lookup_food_codes_short
# from python_functions.get_keyword_list import lookup_food_codes
import python_functions.cleanup_functions as cleanup_functions
from python_functions.build_tree import create_food_tree, label_dataset_with_mapping, label_parent_nodes
from python_functions.fuzzy_node_mapping import get_highest_scoring_matches
from anytree import RenderTree, PreOrderIter
import datetime

#Enter the user input in here, including list items and setting checkboxes
user_input = {
    # "chosenItems": ["2% Milk", "Eggs", "Cheese", "Pasta", "Rice", "Lucky ", "Butter"],  # Example user input as a list
    "chosenItems": ["2% Milk", "White Eggs", "Jasmine Rice", "Bread"],  # Example user input as a list
    "checkboxSodium": False,
    "checkboxSatFat": False,
    "checkboxSugars": False,
    "checkboxAnimalMeats": False,
    "checkboxFruits": False,
    "checkboxVeg": False,
    "checkboxFish": False,
    "checkboxWholeGrains": False,
    "checkboxPlantProt": False
}

# Processing user input into constraints to match column names: 
constraints_mapping = {
    "checkboxSodium": "Sodium/Salt",
    "checkboxSatFat": "Saturated Fat",
    "checkboxSugars": "Added Sugars"
}

checked_boxes = ['Price']
for key, value in constraints_mapping.items():
    if user_input.get(key):
        checked_boxes.append(value)

optimization_cols = ['Price', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
num_checked = len(checked_boxes)
print("Number of checked boxes:", num_checked)
print("Checked boxes:", checked_boxes)

weights = [
    1/num_checked if col in checked_boxes else 0 for col in optimization_cols]
print("Weights:", weights)
print('-------------------')

# Code below is for making the food hierarchy. Option to reprint below
root = create_food_tree('updated_food_hierarchy2.csv')

# # Print the tree
# for pre, _, node in RenderTree(root):
#     print("%s%s" % (pre, node.name))

nodes_list = [node.name for node in PreOrderIter(root)]

# The chosenItems are what the user inputs into the UI
chosenItems = user_input['chosenItems']
print("User Input:")
print(chosenItems)
print("------------------")

# Fuzzy Matching of user input to hierarchy node (highest scoring match)
highest_matches, match_to_filter_df = get_highest_scoring_matches(
    chosenItems, nodes_list)

# Printing Highest Matches and Filtered Words:
# highest_matches = get_highest_scoring_matches(chosenItems, nodes_list)
print("Highest Matches:")
print(highest_matches)
print("------------------")
print("Filtered Words:")
print(match_to_filter_df)

aggregated_recommendations = pd.DataFrame()
aggregated_results = {key: [] for key in cleanup_functions.create_unique_keys(highest_matches)}
unique_keys = list(cleanup_functions.create_unique_keys(highest_matches))
print(aggregated_results)
print(unique_keys)

#----------------------------------------------------------------------------

# Load Dataset and cleanup
main_data = pd.read_csv("updated_11-20-23_walmart_products.csv")
# Create a new column 'ID' with sequential numbers
main_data['ID'] = range(1, len(main_data) + 1)

# Rearrange columns to put 'ID' first
column_order = ['ID'] + \
    [col for col in main_data.columns if col != 'ID']
main_data = main_data[column_order]

#Cleanup Function Applied: 
main_data = cleanup_functions.dataframe_cleanup(main_data)

# Collect level counts for each user input
datasets = label_parent_nodes(highest_matches, root, main_data)

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
saved_dataframes = {}

for key, dataset in datasets.items():
    file_name = f'{key}.csv'
    dataset.to_csv(file_name, index=False)
    print(f"{key} saved to {file_name} (Shape: {dataset.shape})")

#--------------First Recommendation with Filters Applied-------------------------------------

# Filter rows that contain the node in the in the 'Keyword' column
main_data = label_dataset_with_mapping(
    highest_matches, root, main_data)
main_data.to_csv('initial_rec.csv', index=False)


# Build Constraints File:
constraints_list = {"Main_List": {}}
list_item_counts = Counter(highest_matches)
for item, count in list_item_counts.items():
    constraints_list["Main_List"][item] = {"max": count, "min": count}
# Save the dictionary as a JSON file
with open('output_constraints.json', 'w+') as outfile:
    json.dump(constraints_list, outfile, indent=2)

#Cleanup Function: 
filtered_records = cleanup_functions.dataset_converter(main_data, "mapping", "ID")

#Filter Dataset: 
filtered_records = cleanup_functions.filter_records_by_keywords(filtered_records, match_to_filter_df)

#Scale Data:
filtered_records = cleanup_functions.scale_columns(filtered_records, optimization_cols)

# First Recommendation:
opt = NutOptimizer(data=filtered_records)
opt.load_constraints_json("output_constraints.json")
opt.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
first_rec_output = opt.get_all_results()
first_rec_output = first_rec_output["Main_List"]
first_rec_output.to_csv('first_rec.csv', index=False)
upc_codes_to_remove = first_rec_output['UPC Code'].tolist()
cleanup_functions.process_optimization_output(first_rec_output, unique_keys, aggregated_results)

#--------------Second Recommendation without Filters-------------------------------------

dataset2 = main_data[~main_data['UPC Code'].isin(upc_codes_to_remove)]
dataset2 = cleanup_functions.dataset_converter(dataset2, "mapping", "ID")
#Scale Data:
dataset2 = cleanup_functions.scale_columns(dataset2, optimization_cols)

dataset2.to_csv('dataset2.csv', index=False)

opt2 = NutOptimizer(data=dataset2)
opt2.load_constraints_json("output_constraints.json")
opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
second_rec_output = opt2.get_all_results()
second_rec_output = second_rec_output["Main_List"]
upc_codes_to_remove.extend(second_rec_output['UPC Code'].tolist())  # Adding another UPC code# 
second_rec_output.to_csv('second_rec.csv', index=False)
print(upc_codes_to_remove)
cleanup_functions.process_optimization_output(second_rec_output, unique_keys, aggregated_results)

#--------------Third Recommendation-------------------------------------
dataset3 = pd.read_csv("dataset_parent3.csv")
dataset3 = dataset3[~dataset3['UPC Code'].isin(upc_codes_to_remove)]
dataset3 = cleanup_functions.dataset_converter(dataset3, "User_Input", "ID")
#Scale Data:
dataset3 = cleanup_functions.scale_columns(dataset3, optimization_cols)

# dataset3.to_csv('dataset3.csv', index=False)

opt3 = NutOptimizer(data=dataset3)
opt3.load_constraints_json("output_constraints.json")
opt3.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
third_rec_output = opt3.get_all_results()
third_rec_output = third_rec_output["Main_List"]
upc_codes_to_remove.extend(third_rec_output['UPC Code'].tolist())  # Adding another UPC code# 
third_rec_output.to_csv('third_rec.csv', index=False)
print(upc_codes_to_remove)
cleanup_functions.process_optimization_output(third_rec_output, unique_keys, aggregated_results)


#--------------Fourth Recommendation-------------------------------------
dataset4 = pd.read_csv("dataset_parent4.csv")
dataset4 = dataset4[~dataset4['UPC Code'].isin(upc_codes_to_remove)]
dataset4 = cleanup_functions.dataset_converter(dataset4, "User_Input", "ID")
#Scale Data:
dataset4 = cleanup_functions.scale_columns(dataset4, optimization_cols)

# dataset4.to_csv('datset4.csv', index=False)

opt4 = NutOptimizer(data=dataset4)
opt4.load_constraints_json("output_constraints.json")
opt4.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
forth_rec_output = opt4.get_all_results()
forth_rec_output = forth_rec_output["Main_List"]
print(forth_rec_output)
upc_codes_to_remove.extend(forth_rec_output['UPC Code'].tolist())  # Adding another UPC code# 
forth_rec_output.to_csv('forth_rec.csv', index=False)
print(upc_codes_to_remove)
cleanup_functions.process_optimization_output(forth_rec_output, unique_keys, aggregated_results)



#--------------Fifth Recommendation-------------------------------------
dataset5 = pd.read_csv("dataset_parent5.csv")
dataset5 = dataset5[~dataset5['UPC Code'].isin(upc_codes_to_remove)]
dataset5 = cleanup_functions.dataset_converter(dataset5, "User_Input", "ID")
#Scale Data:
dataset5 = cleanup_functions.scale_columns(dataset5, optimization_cols)

dataset5.to_csv('dataset5.csv', index=False)

opt5 = NutOptimizer(data=dataset5)
opt5.load_constraints_json("output_constraints.json")
opt5.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
fifth_rec_output = opt5.get_all_results()
fifth_rec_output = fifth_rec_output["Main_List"]
upc_codes_to_remove.extend(fifth_rec_output['UPC Code'].tolist())  # Adding another UPC code# 
fifth_rec_output.to_csv('fifth_rec.csv', index=False)
print(upc_codes_to_remove)
cleanup_functions.process_optimization_output(fifth_rec_output, unique_keys, aggregated_results)


#--------------Sixth Recommendation-------------------------------------
dataset6 = pd.read_csv("dataset_parent6.csv")
dataset6 = dataset6[~dataset6['UPC Code'].isin(upc_codes_to_remove)]
dataset6 = cleanup_functions.dataset_converter(dataset6, "User_Input", "ID")
#Scale Data:
dataset6 = cleanup_functions.scale_columns(dataset6, optimization_cols)

# dataset6.to_csv('dataset6.csv', index=False)

opt6 = NutOptimizer(data=dataset6)
opt6.load_constraints_json("output_constraints.json")
opt6.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
# opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
sixth_rec_output = opt6.get_all_results()
sixth_rec_output = sixth_rec_output["Main_List"]
upc_codes_to_remove.extend(sixth_rec_output['UPC Code'].tolist())  # Adding another UPC code# 
sixth_rec_output.to_csv('sixth_rec.csv', index=False)
print(upc_codes_to_remove)
cleanup_functions.process_optimization_output(sixth_rec_output, unique_keys, aggregated_results)


print(aggregated_results)

# Define a function to process and append each recommendation
def process_and_append_recommendation(rec_df, rec_number, aggregated_df):
    rec_df['rec number'] = rec_number  # Add the recommendation number
    return pd.concat([aggregated_df, rec_df], ignore_index=True)

# Process each recommendation and append to the aggregated DataFrame
for i, rec_output in enumerate([first_rec_output, second_rec_output, third_rec_output, 
                                forth_rec_output, fifth_rec_output, sixth_rec_output], start=1):
    
    # Process the recommendation output. Ensure this function modifies the DataFrame in place or returns a modified DataFrame
    cleanup_functions.process_optimization_output(rec_output, unique_keys, aggregated_results)

    # Check if rec_output is a DataFrame, then proceed
    if isinstance(rec_output, pd.DataFrame):
        rec_output['rec. number'] = i  # Add the recommendation number
        aggregated_recommendations = pd.concat([aggregated_recommendations, rec_output], ignore_index=True)
    else:
        print(f"Recommendation {i} did not return a DataFrame.")

# Save the aggregated DataFrame to a CSV file
aggregated_recommendations.to_csv('aggregated_recommendations.csv', index=False)

