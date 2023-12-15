import json
from collections import Counter
from sklearn.preprocessing import StandardScaler
from Optimizer2 import NutOptimizer
import pandas as pd
from python_functions.get_food_code import get_food_codes, lookup_food_codes_short
import python_functions.cleanup_functions as cleanup_functions
from hashTable.food_tree import create_food_tree, get_level2_descriptions, get_grandparent_level_descriptions, get_grandparent_nodes, get_parent_nodes
from anytree import Node, RenderTree, PreOrderIter
import datetime

def generateRecommendations(form_data, requested_constraiints):
    # print(requested_contraints)

    #Creating Tree:
    target_dir = ""

    root, name_to_node = create_food_tree(
    schema_file=target_dir+'schema.csv',
    food_file=target_dir+'food.csv',
    survey_file=target_dir+'survey_fndds_food.csv',
    wweia_file=target_dir+'wweia_food_category.csv')

    chosenItems = form_data['chosenItems']
    # print(chosenItems)
    food_codes = get_food_codes(chosenItems)
    # print(food_codes)
    descriptions = lookup_food_codes_short(food_codes, target_dir+'hashTable/mergedFNDDS.csv')
    # print(descriptions)
    chosen_item_order = {item: i for i, item in enumerate(descriptions)}
    # print(chosen_item_order)

    level2_descriptions = get_level2_descriptions(root, name_to_node, descriptions)
    # print(level2_descriptions)
    level1_descriptions = get_grandparent_level_descriptions(root, name_to_node, descriptions)
    # print(level1_descriptions)
    parent_nodes = get_parent_nodes(name_to_node, descriptions)
    # print(parent_nodes)
    grandparent_nodes = get_grandparent_nodes(name_to_node, descriptions)
    # print(grandparent_nodes)

    chosen_item_order_level2 = {item: i for i, item in enumerate(parent_nodes)}
    chosen_item_order_level1 = {item: i for i, item in enumerate(grandparent_nodes)}
    # print(chosen_item_order_level1)

    main_data = pd.read_csv(target_dir+'database_cleaned_fullgrocery_with_parents.csv')
    # Assuming database_cleaned_fullgrocery_with_parents is your DataFrame
    main_data.rename(columns={'ID': 'ID_x'}, inplace=True)

    # Filter rows that contain the descriptions in the 'Keyword' column
    Level3 = main_data[main_data['Keyword'].isin(descriptions)]
    ####
    #  TODO:
    #  Error handling for when there is no keyword in description
    ####

    output = {"Main_List": {}}
    output_level2 = {"Main_List_Level2": {}}
    output_Level1 = {"Main_List_Level1": {}}

    item_counts = Counter(descriptions)  # Gets count of each list item
    Level2_Counts = Counter(parent_nodes)  # Gets count of each list item
    Level1_Counts = Counter(grandparent_nodes)  # Gets count of each list item

    # Build constraints for each level of the hierarchy: 
    for item, count in item_counts.items():
        output["Main_List"][item] = {"max": count, "min": count}

    # Save the dictionary as a JSON file
    with open(target_dir+'output_constraints.json', 'w+') as outfile:
        json.dump(output, outfile, indent=2)

    # Create JSON Dictionary of List Items for Level2
    for item, count in Level2_Counts.items():
        output_level2["Main_List_Level2"][item] = {"max": count, "min": count}

    # Save the dictionary as a JSON file
    with open(target_dir+'output_constraints_Level2.json', 'w+') as outfile2:
        json.dump(output_level2, outfile2, indent=2)

            # Create JSON Dictionary of List Items for Level2
    for item, count in Level1_Counts.items():
        output_Level1["Main_List_Level1"][item] = {"max": count, "min": count}

    # Save the dictionary as a JSON file
    with open(target_dir+'output_constraints_Level1.json', 'w+') as outfile3:
        json.dump(output_Level1, outfile3, indent=2)

    # Import CSV and Read CSV
    Level3 = cleanup_functions.dataset_converter(Level3, "Keyword", "ID_x")        
    Level3 = cleanup_functions.dataframe_cleanup(Level3)
    Level3.to_csv(target_dir+'test_cleanup.csv', index=False)

    #Scale all of the Hierarchy Levels: 
    scaler = StandardScaler()
    optimization_cols = ['Price per Serving', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
    Level3[optimization_cols] = scaler.fit_transform(Level3[optimization_cols])
    Level3.to_csv(target_dir+'Level3_main_database_file.csv', index =False)
            
    num_checked = len(requested_contraints)
    weights = [1/num_checked if col in requested_contraints else 0 for col in optimization_cols]

    if Level3.empty:
        print("Level3 DataFrame is empty!")

    #First Recommendation: 
    opt = NutOptimizer(data=Level3)
    opt.load_constraints_json(target_dir+"output_constraints.json")
    opt.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
    Level3_data_output = opt.get_all_results()
    Level3_data_output = Level3_data_output["Main_List"]
    Level3_data_output['image_url'] = Level3_data_output['ID_x'].apply(cleanup_functions.id_to_url)
    # Create a new column in the DataFrame that contains the order of each row
    Level3_data_output['Order'] = Level3_data_output['Keyword'].map(chosen_item_order)
    # Sort the DataFrame by the new column
    Level3_data_output = Level3_data_output.sort_values('Order')
    print(Level3_data_output)
    Level3_data_output.to_csv(target_dir+'Level3_data_output.csv', index=False)
    id_list = Level3_data_output['ID_x'].tolist()
    print(id_list)
    
    #Level 2 Data Cleanup
    Level2 = main_data[main_data['Keyword'].isin(level2_descriptions)]
    # Level2 = Level2[~Level2['ID_x'].isin([605021299183, 11110092205])]
    Level2 = Level2[~Level2['ID_x'].isin(id_list)]
    Level2 = cleanup_functions.dataset_converter(Level2, "Parent", "ID_x")        
    Level2 = cleanup_functions.dataframe_cleanup(Level2)
    Level2[optimization_cols] = scaler.fit_transform(Level2[optimization_cols])
    Level2.to_csv(target_dir+'Level2_main_database_file.csv', index =False)

    #Second Recommendation: 
    opt2 = NutOptimizer(data=Level2)
    opt2.load_constraints_json(target_dir+"output_constraints_Level2.json")
    opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
    Level2_data_output = opt2.get_all_results()
    Level2_data_output = Level2_data_output["Main_List_Level2"]  
    Level2_data_output['image_url'] = Level2_data_output['ID_x'].apply(cleanup_functions.id_to_url)
    Level2_data_output['Order'] = Level2_data_output['Parent'].map(chosen_item_order_level2)
    # Sort the DataFrame by the new column
    Level2_data_output = Level2_data_output.sort_values('Order')
    id_list2 = Level2_data_output['ID_x'].tolist()
    id_list2 = id_list2 + id_list

    #Level 1 Cleanup: 
    Level1 = main_data[main_data['Keyword'].isin(level1_descriptions)]
    # Import CSV and Read CSV
    Level1 = Level1[~Level1['ID_x'].isin(id_list2)]
    Level1 = cleanup_functions.dataset_converter(Level1, "Grandparent", "ID_x")
    Level1 = cleanup_functions.dataframe_cleanup(Level1)
    Level1[optimization_cols] = scaler.fit_transform(Level1[optimization_cols])
    Level1.to_csv(target_dir+'Level1_main_database_file.csv', index =False)


    #Third Recommendation
    opt3 = NutOptimizer(data=Level1)
    opt3.load_constraints_json(target_dir+"output_constraints_Level1.json")
    opt3.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
    Level1_data_output = opt3.get_all_results()
    Level1_data_output = Level1_data_output["Main_List_Level1"] 
    Level1_data_output['image_url'] = Level1_data_output['ID_x'].apply(cleanup_functions.id_to_url)

    Level1_data_output['Order'] = Level1_data_output['Grandparent'].map(chosen_item_order_level1)
    # Sort the DataFrame by the new column
    Level1_data_output = Level1_data_output.sort_values('Order')



    data_dict = Level3_data_output.to_dict()
    Level3_data_list = Level3_data_output.to_dict('records')
    Level2_data_list = Level2_data_output.to_dict('records')
    Level1_data_list = Level1_data_output.to_dict('records')
    
    # Create a list to hold all the dictionaries
    recommendations = []

    # Get the max order number across all levels
    max_order = max(max(Level3_data_output['Order']), max(Level2_data_output['Order']), max(Level1_data_output['Order']))

    # Loop through all the order numbers
    for order in range(max_order + 1):
        # Create a dictionary to hold the current order's recommendations
        recommendation = {}

        # Get the descriptions for the current order number and add them to the dictionary
        for level1 in Level1_data_list:
            if level1['Order'] == order:
                recommendation['Level1'] = level1
                break
        for level2 in Level2_data_list:
            if level2['Order'] == order:
                recommendation['Level2'] = level2
                break
        for level3 in Level3_data_list:
            if level3['Order'] == order:
                recommendation['Level3'] = level3
                break

        # Add the dictionary to the list
        recommendations.append(recommendation)

    # Concatenate dataframes
    full_data_output = pd.concat([Level3_data_output, Level2_data_output, Level1_data_output])

    # Create a dictionary where each key is an order, and the value is a list of products (each product being a dictionary of its data)
    grouped_data = full_data_output.groupby('Order').apply(lambda x: x.to_dict('records')).to_dict()

    timestamp = str(datetime.datetime.now())
    
    try: 
        with open(target_dir+'products_output.json', 'r') as infile: 
            contents = json.load(infile)
    except FileNotFoundError:
        contents = {}
    except json.JSONDecodeError: 
        contents = {}
      # should generate a string with the date and time
    with open(target_dir+'products_output.json', 'w') as outfile:
        # contents = {}
        # # if there is anything in the file, attempt to load it. Otherwise, file is empty
        # if outfile.read(1):  
        #     contents = json.load(outfile)

        contents[timestamp] = data_dict
        json.dump(contents, outfile, indent=2)
    
    return Level3_data_output, grouped_data
