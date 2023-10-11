import requests
import pandas as pd
import time
import json
from pandas import json_normalize

def get_food_codes(food_list):
    base_url = "https://api.nal.usda.gov/fdc/v1/foods/search"
    headers = {"Content-Type": "application/json"}
    api_calls = 0
    food_codes = []

    for food_name in food_list:
        params = {
            "query": food_name,
            "pageSize": 100,
            "pageNumber": 1,
            "api_key": 'E1ouQwGe4U2PPyeuzAbIH2sbVSVMwDepw1Hngeor',
        }

        response = requests.get(base_url, headers=headers, params=params)
        response_json = response.json()

        try:
            foods = response_json["foods"]
        except KeyError as e:
            continue

        top_food = None
        for food in foods:
            try:
                if food["dataType"] == "Survey (FNDDS)":
                    top_food = food
                    break
            except Exception as e:
                continue

        if top_food is not None:
            try:
                top_food_code = str(top_food["foodCode"])
            except Exception as e:
                continue
            else:
                food_codes.append(top_food_code)
        else:
            print(f"No food of type 'Survey (FNDDS)' was found for {food_name}.")

    return food_codes

def lookup_food_codes(food_codes_list, data_file):
    # Read the data file into a pandas DataFrame
    df = pd.read_csv(data_file, dtype={'food_code': str})  # Make sure 'food_code' column is read as string

    # Check if 'food_code' and 'short_description' columns exist in the DataFrame
    if 'food_code' not in df.columns or 'description' not in df.columns:
        raise ValueError("'food_code' or 'description' does not exist in the DataFrame.")

    # Filter the DataFrame to get only the rows where food_code is in the food_codes_list
    filtered_df = df[df['food_code'].isin(food_codes_list)]

    # Set the DataFrame's index to the food_code column
    filtered_df.set_index('food_code', inplace=True)

    # Re-index the DataFrame using the original food_codes_list, this will ensure the order is preserved
    filtered_df = filtered_df.reindex(food_codes_list)

    # Get the list of 'short_description' corresponding to the food codes
    descriptions_list = filtered_df['description'].tolist()

    return descriptions_list

def lookup_food_codes_short(food_codes_list, data_file):
    # Read the data file into a pandas DataFrame
    df = pd.read_csv(data_file, dtype={'food_code': str})  # Make sure 'food_code' column is read as string

    # Check if 'food_code' and 'short_description' columns exist in the DataFrame
    if 'food_code' not in df.columns or 'short_description' not in df.columns:
        raise ValueError("'food_code' or 'short_description' does not exist in the DataFrame.")

    # Filter the DataFrame to get only the rows where food_code is in the food_codes_list
    filtered_df = df[df['food_code'].isin(food_codes_list)]

    # Set the DataFrame's index to the food_code column
    filtered_df.set_index('food_code', inplace=True)

    # Re-index the DataFrame using the original food_codes_list, this will ensure the order is preserved
    filtered_df = filtered_df.reindex(food_codes_list)

    # Get the list of 'short_description' corresponding to the food codes
    short_descriptions_list = filtered_df['short_description'].tolist()

    return short_descriptions_list

# Usage:
food_list = ["Apples", "Kraft Mac and Cheese"]
food_codes = get_food_codes(food_list)
print(food_codes)


# Usage:
# food_list = ["Kroger® 93% Lean Ground Beef", "another food name", "..."]
# api_key = "your_api_key_here"
# food_codes = get_food_codes(food_list, api_key)
# print(food_codes)
