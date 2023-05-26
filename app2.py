from flask import Flask, render_template, request
import json
import csv
from collections import Counter
from sklearn.preprocessing import StandardScaler
# from NutOptimizer import NutOptimizer
from Optimizer2 import NutOptimizer
import pandas as pd
import cleanup_functions
import datetime

app = Flask(__name__)
# Disable caching of pages, always return newest version of page
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

# This is the list of items presented to the user to choose from: 
file = open('category_cleanup.json')
data = json.load(file)
data = data['branded_food_category']
file.close()

@app.route("/")
def index():
    categories_with_separator = [category + '$#^' for category in data]
    return render_template('MultiObjModel/index_MO.html', data=categories_with_separator)


@app.route("/recommendations", methods=["GET", "POST"])
def recommendations():
    if request.method == "GET":
        return render_template('MultiObjModel/recommendations_MO.html', test="get", data={})
    elif request.method == "POST":
        # 0. Retrieve data from Flask form
        form_data = dict(request.form)

        # List of form names for sliders
        slider_form_names = ['weightPrice', 'weightSodium', 'weightSatFat', 'weightSugars']

        # Get descriptions for each slider value and store them in a list
        slider_descriptions = [cleanup_functions.convert_to_description(request.form[name]) for name in slider_form_names]
        print(slider_descriptions)

        budget_amount = request.form["budgetAmount"]
        
        chosenItems = request.form['chosenItems']
        chosenItems = chosenItems.split("#^$")
        # pop the last item off the list, which is an empty string
        chosenItems.pop(-1)
        # print(chosenItems)

        output = {"Main_List": {}}
        for category in data:
            output["Main_List"][category] = {"max": 0, "min": 0}

        if request.form.get("budgetAmount", True):  
            print(budget_amount)
            output["Main_List"]["Price"] = {"max": int(budget_amount), "min": 0}  # assigning max values from mapping above
        else:
            pass
               
        # 1. Create JSON file of results
        # with open("test.json", "w") as file:
        #     json.dump(constraints, file, indent=2)

        item_counts = Counter(chosenItems)  # Gets count of each list item
        # print(item_counts)
        # Create JSON Dictionary of List Items
        for item, count in item_counts.items():
            output["Main_List"][item] = {"max": count, "min": count}

        # Save the dictionary as a JSON file
        with open('output_constraints.json', 'w+') as outfile:
            json.dump(output, outfile, indent=2)
        # Import CSV and Read CSV
        
        df = cleanup_functions.dataset_converter("fdc_kroger_combined_per_serving.csv", "branded_food_category", "ID")        
        df = cleanup_functions.dataframe_cleanup(df)

        wic = pd.read_excel('WIC.xlsx', dtype={'UPC_Code': str})

        wic = wic[['CATEGORY CODE', 'CATEGORY DESCRIPTION', 'SUBCATEGORY CODE',
            'SUBCATEGORY DESCRIPTION', 'UPC CODE', 'BRAND NAME', 'FOOD DESCRIPTION',
            'PACKAGE SIZE', 'UNIT OF MEASURE']]

        wic = wic.rename(columns={'CATEGORY CODE': 'CATEGORY_CODE', 'CATEGORY DESCRIPTION': 'CATEGORY_DESCRIPTION', 
                                'SUBCATEGORY CODE': 'SUBCATEGORY_CODE', 'SUBCATEGORY DESCRIPTION': 'SUBCATEGORY_DESCRIPTION',
                                'UPC CODE': 'UPC_CODE', 'BRAND NAME': 'BRAND_NAME',
                                'FOOD DESCRIPTION': 'FOOD_DESCRIPTION', 'PACKAGE SIZE': 'PACKAGE_SIZE',
                                'UNIT OF MEASURE': 'UNIT_OF_MEASURE'})
        
        def remove_leading_zeroes(cell: str):
            if cell[0] == '0':
                return remove_leading_zeroes(cell[1:])
            return cell

        # wic['UPC_CODE'] = wic['UPC_CODE'].astype(str).apply(get_check_digit)
        wic['UPC_CODE'] = wic['UPC_CODE'].astype(str).apply(remove_leading_zeroes)

        wic_upc_set = set(wic['UPC_CODE'])
        df['is_matched'] = df['gtin_upc'].astype(str).isin(wic_upc_set).astype(int)
        df.to_csv('testofwic.csv', index =False)

        scaler = StandardScaler()
        optimization_cols = ['Price per Serving', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
        df[optimization_cols] = scaler.fit_transform(df[optimization_cols])
        df.to_csv('main_database_file.csv', index =False)

        weights = cleanup_functions.compute_weights(slider_descriptions)
        print(weights)

        opt = NutOptimizer(data=df)
        opt.load_constraints_json("output_constraints.json")
        opt.optimize_all(optimization_cols, weights, verbose=False, var_type='INTEGER')
        data_output = opt.get_all_results()
        data_output = data_output["Main_List"]  # extract the dataframe from the dictionary output

        #Nut Optimizer: 
        # opt = NutOptimizer(data=df)
        # opt.load_constraints_json("output_constraints.json")
        # opt.optimize_all('Price per Serving', verbose=False, var_type='INTEGER')
        # data_output = opt.get_all_results()
        # data_output = data_output["Main_List"]  # extract the dataframe from the dictionary output
        
        # output_int_cost = opt.get_all_optimal_values('Price per Serving')

        data_dict = data_output.to_dict()
        
        timestamp = str(datetime.datetime.now())
        
        try: 
            with open('products_output.json', 'r') as infile: 
                contents = json.load(infile)
        except FileNotFoundError:
            contents = {}
        except json.JSONDecodeError: 
            contents = {}
          # should generate a string with the date and time
        with open('products_output.json', 'w') as outfile:
            # contents = {}
            # # if there is anything in the file, attempt to load it. Otherwise, file is empty
            # if outfile.read(1):  
            #     contents = json.load(outfile)

            contents[timestamp] = data_dict
            json.dump(contents, outfile, indent=2)

        # TODO: Change appearence of data output dictionary: 
        data_recommendation = data_output.to_dict(orient='records')

        # data_recommendation = data_output[['ID', 'Description']].to_dict(orient='records')
    

        
        # print(output_int_cost)
        # level2_integer_fem_res = round(opt.get_one_optimal_value("Main_List", "Price per Serving"),2)
        # pd.DataFrame(output_int_cost['Main List'])[['ID', 'Description', 'branded_food_category', 'Price per Serving', 'Amount']]

        # int_cost = opt.get_all_optimal_values('Price per Serving')
        # output = round(opt.get_one_optimal_value("Price per Serving"),2)
        # pd.DataFrame(int_res['F 31-50'])[['ID', 'Description', 'branded_food_category', 'Price per Serving', 'Amount']]



        #Set Min/Max Constraints
        #Combine all the constraints together?
        #We can do this in the model file
        
        # TEST MODEL: 
        # level_2_opt.optimize_all('Price per Serving', verbose=False, var_type='INTEGER')
        # level_2_int_res = level_2_opt.get_all_results()
        # level_2_int_cost = level_2_opt.get_all_optimal_values('Price per Serving')

        # print("Level 2 Data - F 31-50 - Integer Optimization - With Category Constraints")
        # level2_integer_fem_res = round(level_2_opt.get_one_optimal_value("F 31-50", "Price per Serving"),2)
        # level2_integer_male_res = round(level_2_opt.get_one_optimal_value("M 31-50", "Price per Serving"),2)
        # pd.DataFrame(level_2_int_res['F 31-50'])[['ID', 'Description', 'branded_food_category', 'Price per Serving', 'Amount']]

        output_as_html = data_output.to_html()
        return render_template('MultiObjModel/recommendations_MO.html', data=data_recommendation, html_output=output_as_html)


app.run(debug=True, port=5120)

# Categories:
# {
#     "Baking/cooking Mixes/supplies" {
#       "max": 2
#     },
#     "Bread and Buns": {
#       "max": 1
#     },
#     "Canned Vegetable": {
#       "max": 1
#     },
#     "Cereal": {
#       "max": 1
#     }
#   }

#possible file cleanup
# dat = dat.fillna(0)

# rename_dict = {
#                'Protein': 'Protein - g',
#                'Carbohydrate, by difference': "Total Carbohydrate"
#               }

# dat = dat.rename(rename_dict, axis=1)

# # Conversions: sugar from g to kcal, total lipid g to kcal, Fatty acids total saturated g to kcal, Vitamin A iu to mcg RAE
# dat['Protein - cal'] = dat['Protein - g'] * 4 
# dat['Carb - cal'] = dat['Total Carbohydrate'] * 4
# dat['Total lipid (fat)'] *= 9
# dat['Fatty acids, total saturated'] *= 9
# dat['Sugars, total including NLEA'] *= 4
# dat['Sugars, added'] *= 4
# dat['Price per Serving'] = round(dat['Price'] / dat['No Servings'], 2)