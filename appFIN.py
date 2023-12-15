from flask import Flask, render_template, request
import json
import csv
from collections import Counter
from sklearn.preprocessing import StandardScaler
from Optimizer2 import NutOptimizer
import pandas as pd
from python_functions.get_food_code import get_food_codes, lookup_food_codes_short
# from python_functions.get_keyword_list import lookup_food_codes
import python_functions.cleanup_functions as cleanup_functions
from hashTable.food_tree import create_food_tree, get_level2_descriptions, get_grandparent_level_descriptions, get_grandparent_nodes, get_parent_nodes
from anytree import Node, RenderTree, PreOrderIter
import datetime
from recommendationEngine import generateRecommendations

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
        # TODO: Change appearence of data output dictionary:

        # prepare chosenItems
        form_data = dict(request.form)
        form_data['chosenItems'] = form_data['chosenItems'].split("#^$")
        # pop the last item off the list, which is an empty string
        form_data['chosenItems'].pop(-1)

        # parse requested constraints
        constraints_mapping = {
            "checkboxSodium": "Sodium/Salt",
            "checkboxSatFat": "Saturated Fat",
            "checkboxSugars": "Added Sugars"
            }

        requested_contraints = ['Price per Serving']  # Always include 'Price per Serving'

        for key, value in constraints_mapping.items():
            if form_data.get(key):
                print('value',value)
                requested_contraints.append(value)

        level3_data_output, grouped_data = generateRecommendations(form_data, requested_constraints)
        data_recommendation = level3_data_output.to_dict(orient='records')
        output_as_html = level3_data_output.to_html()
        # return render_template('recommendations.html', data=data_recommendation, html_output=output_as_html)
        return render_template('recommendations.html', data=grouped_data, html_output=output_as_html)

app.run(debug=True, port=5510)

