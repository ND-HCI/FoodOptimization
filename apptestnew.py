from flask import Flask, render_template, request
import json
import csv
from collections import Counter
from sklearn.preprocessing import StandardScaler
from Optimizer2 import NutOptimizer
import pandas as pd
from python_functions.get_food_code import get_food_codes, lookup_food_codes, lookup_food_codes_short
# from python_functions.get_keyword_list import lookup_food_codes
import python_functions.cleanup_functions as cleanup_functions
from python_functions.build_tree import create_food_tree, label_dataset_with_mapping
from python_functions.fuzzy_node_mapping import get_highest_scoring_matches
from anytree import RenderTree, PreOrderIter
import datetime

app = Flask(__name__)
# Disable caching of pages, always return newest version of page
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    if request.method == "GET":
        return render_template('recommendations.html', test="get", data={})
    elif request.method == "POST":

        constraints_mapping = {
            "checkboxSodium": "Sodium/Salt",
            "checkboxSatFat": "Saturated Fat",
            "checkboxSugars": "Added Sugars"
            }

        checked_boxes = ['Price']  # Always include 'Price per Serving'

        for key, value in constraints_mapping.items():
            if request.form.get(key):
                checked_boxes.append(value)

        print(checked_boxes)

        # Code below is for making the food hierarchy. Option to reprint below
        root = create_food_tree('updated_food_hierarchy.csv')  

        # Print the tree
        for pre, _, node in RenderTree(root):
            print("%s%s" % (pre, node.name))

        nodes_list = [node.name for node in PreOrderIter(root)]

        #The chosenItems are what the user inputs into the UI
        chosenItems = request.form['chosenItems']
        chosenItems = chosenItems.split("#^$")        # pop the last item off the list, which is an empty string
        chosenItems.pop(-1)
        print(chosenItems)
        print("------------------")

        #Fuzzy Matching of user input to hierarchy node (highest scoring match)
        highest_matches, match_to_filter_df = get_highest_scoring_matches(chosenItems, nodes_list)

        #Printing Highest Matches and Filtered Words: 
        # highest_matches = get_highest_scoring_matches(chosenItems, nodes_list)
        print("Highest Matches:")
        print(highest_matches)
        print("------------------")
        print("Filtered Words:")
        print(match_to_filter_df)

        #Load Dataset
        main_data = pd.read_csv("merged_walmart_data.csv")
        # Create a new column 'ID' with sequential numbers
        main_data['ID'] = range(1, len(main_data) + 1)

        # Rearrange columns to put 'ID' first
        column_order = ['ID'] + [col for col in main_data.columns if col != 'ID']
        main_data = main_data[column_order]

        # Filter rows that contain the node in the in the 'Keyword' column
        main_data = label_dataset_with_mapping(highest_matches, root, main_data)

        #Preview Dataset:
        main_data.to_csv('preview_test_data.csv', index =False)

        #Build Constraints File: 
        constraints_list = {"Main_List": {}}
        keyword_counts = Counter(highest_matches)
        for item, count in keyword_counts.items():
            constraints_list["Main_List"][item] = {"max": count, "min": count}
                # Save the dictionary as a JSON file
        with open('output_constraints.json', 'w+') as outfile:
            json.dump(constraints_list, outfile, indent=2)

        # Import CSV and Read CSV
        main_data = cleanup_functions.dataset_converter(main_data, "mapping", "ID")        
        main_data = cleanup_functions.dataframe_cleanup(main_data)
        main_data.to_csv('test_data/keyword_test_cleanup.csv', index=False)

        filtered_records = pd.DataFrame()

        # Convert all product names to lowercase for case-insensitive matching
        product_names_lower = main_data['Product Name'].str.lower()
        # Flatten the list of lists into a single list of keywords
        keywords = [word.lower() for sublist in match_to_filter_df for word in sublist]
        # Check if any keyword is in the Product Name
        contains_keyword = product_names_lower.apply(lambda name: any(keyword in name for keyword in keywords))

        # If any keyword is present, filter the data
        if contains_keyword.any():
            filtered_records = main_data[contains_keyword]
        else:
            # If no keyword is present, do not filter the data
            filtered_records = main_data

        # Save the filtered DataFrame
        filtered_records.to_csv('initial_rec.csv', index=False)

        #Scale 
        scaler = StandardScaler()
        optimization_cols = ['Price', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
        filtered_records[optimization_cols] = scaler.fit_transform(filtered_records[optimization_cols])
        filtered_records.to_csv('main_recommendation.csv', index =False)

        num_checked = len(checked_boxes)
        print("Number of checked boxes:", num_checked)
        print("Checked boxes:", checked_boxes)

        weights = [1/num_checked if col in checked_boxes else 0 for col in optimization_cols]
        print("Optimization columns:", optimization_cols)
        print("Weights:", weights)

        #First Recommendation: 
        opt = NutOptimizer(data=filtered_records)
        opt.load_constraints_json("output_constraints.json")
        opt.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
        # opt.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
        keyword_output = opt.get_all_results()
        keyword_output = keyword_output["Main_List"]
        keyword_output['image_url'] = keyword_output['ID'].apply(cleanup_functions.id_to_url)

        # #With Foodcode Output
        # opt2 = NutOptimizer(data=food_code_data)
        # opt2.load_constraints_json("test_data/foodcode_output_constraints.json")
        # opt2.optimize_all(optimization_cols, weights, verbose=False, var_type='integer')
        # # opt.optimize_all(optimization_cols, weights, verbose=False, var_type='binary')
        # foodcode_output = opt2.get_all_results()
        # foodcode_output = foodcode_output["Main_List"]
        # foodcode_output['image_url'] = foodcode_output['ID'].apply(cleanup_functions.id_to_url)


        # # Create a new column in the DataFrame that contains the order of each row
        # Level3_data_output['Order'] = Level3_data_output['Keyword'].map(chosen_item_order)
        # # Sort the DataFrame by the new column
        # Level3_data_output = Level3_data_output.sort_values('Order')
        keyword_output.to_csv('test_data/keyword_data_output.csv', index=False)
        keyword_output_id_list = keyword_output['ID'].tolist()

        # foodcode_output.to_csv('test_data/foodcode_data_output.csv', index=False)
        # keyword_output_id_list = keyword_output['ID'].tolist()
        
        # TODO: Change appearence of data output dictionary: 
        data_recommendation = {"Main_List": keyword_output.to_dict(orient='records')}
        # data_recommendation2 = {"Main_List": foodcode_output.to_dict(orient='records')}


        output_as_html = keyword_output.to_html()
        # output_as_html2 = foodcode_output.to_html()

        # return render_template('recommendations.html', data=data_recommendation, html_output=output_as_html)
        return render_template('recommendations.html', data=data_recommendation, html_output=output_as_html)

app.run(debug=True, port=5513
        )

