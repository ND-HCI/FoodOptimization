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
from hashTable.food_tree import create_food_tree, get_level2_descriptions, get_grandparent_level_descriptions, get_grandparent_nodes, get_parent_nodes
from anytree import Node, RenderTree, PreOrderIter
import datetime

app = Flask(__name__)
# Disable caching of pages, always return newest version of page
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# This is the list of items presented to the user to choose from: 
# TODO: Going to keep this in here since this is for what will be displayed in dropdown
file = open('category_cleanup.json')
data = json.load(file)
data = data['branded_food_category']
file.close()

#TODO: replace with json codes 
#Test JSON LIST of foodcodes: 
food_code_file = open('foodcode_output.json')
json_test = json.load(food_code_file)
json_test = json_test['Keyword']
food_code_file.close()

@app.route("/")
def index():
    # Opening branded_food_category and adding separator to the end of each category
    # Again, used for the dropdown
    # TODO: might want to change the dropdown 
    categories_with_separator = [category + '$#^' for category in data]
    return render_template('index.html', data=categories_with_separator)

@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    if request.method == "GET":
        return render_template('recommendations.html', test="get", data={})
    elif request.method == "POST":
        # 0. Retrieve data from Flask form
        form_data = dict(request.form)

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

        #Creating Tree: 
        root, name_to_node = create_food_tree(
        schema_file='schema.csv',
        food_file='food.csv',
        survey_file='survey_fndds_food.csv',
        wweia_file='wweia_food_category.csv')

        chosenItems = request.form['chosenItems']
        chosenItems = chosenItems.split("#^$")        # pop the last item off the list, which is an empty string
        chosenItems.pop(-1)
        print(chosenItems)
        print("------------------")
        food_codes = get_food_codes(chosenItems)
        print(food_codes)
        print("------------------")
        descriptions = lookup_food_codes(food_codes, 'hashTable/mergedFNDDS.csv')
        short_descriptions = lookup_food_codes_short(food_codes, 'hashTable/mergedFNDDS.csv')
        print(descriptions)
        print("------------------")
        print(short_descriptions)
        print("------------------")
        if short_descriptions:  # check if the list is not empty to avoid IndexError
            print(type(short_descriptions[0]))
        else:
            print("The food_codes list is empty.")

        main_data = pd.read_csv('test_data/Test_Optimizer_Data.csv')
        main_data['Food_Code'] = main_data['Food_Code'].astype(str)

        # Filter rows that contain the descriptions in the 'Keyword' column
        keyword = main_data[main_data['Keyword'].isin(short_descriptions)]
        food_code = main_data[main_data['Food_Code'].isin(food_codes)]

        keyword.to_csv('test_data/keyword_test_data.csv', index =False)
        food_code.to_csv('test_data/food_codes_test_data.csv', index =False)

        keyword_output = {"Main_List": {}}
        food_code_output = {"Main_List": {}}

        keyword_counts = Counter(short_descriptions)
        food_code_counts = Counter(food_codes)

        for item, count in keyword_counts.items():
            keyword_output["Main_List"][item] = {"max": count, "min": count}

                # Save the dictionary as a JSON file
        with open('test_data/keyword_output_constraints.json', 'w+') as outfile:
            json.dump(keyword_output, outfile, indent=2)

        for item, count in food_code_counts.items():
            food_code_output["Main_List"][item] = {"max": count, "min": count}

        # Save the dictionary as a JSON file
        with open('test_data/foodcode_output_constraints.json', 'w+') as outfile2:
            json.dump(food_code_output, outfile2, indent=2)

        # Import CSV and Read CSV
        keyword_data = cleanup_functions.dataset_converter(keyword, "Keyword", "ID")        
        keyword_data = cleanup_functions.dataframe_cleanup(keyword_data)
        keyword_data.to_csv('test_data/keyword_test_cleanup.csv', index=False)

        # Import CSV and Read CSV
        food_code_data = cleanup_functions.dataset_converter(food_code, "Food_Code", "ID")        
        food_code_data = cleanup_functions.dataframe_cleanup(food_code_data)
        food_code_data.to_csv('test_data/food_code_test_cleanup.csv', index=False)

        #Scale 
        scaler = StandardScaler()
        optimization_cols = ['Price', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
        keyword_data[optimization_cols] = scaler.fit_transform(keyword_data[optimization_cols])
        keyword_data.to_csv('test_data/keyword_main_database_file.csv', index =False)
        food_code_data[optimization_cols] = scaler.fit_transform(food_code_data[optimization_cols])
        food_code_data.to_csv('test_data/food_code_main_database_file.csv', index =False)

        num_checked = len(checked_boxes)
        print("Number of checked boxes:", num_checked)
        print("Checked boxes:", checked_boxes)

        weights = [1/num_checked if col in checked_boxes else 0 for col in optimization_cols]
        print("Optimization columns:", optimization_cols)
        print("Weights:", weights)

        #First Recommendation: 
        opt = NutOptimizer(data=keyword_data)
        opt.load_constraints_json("test_data/keyword_output_constraints.json")
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

app.run(debug=True, port=5505
        )

