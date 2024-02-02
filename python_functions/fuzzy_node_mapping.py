import pickle
from fuzzywuzzy import process
import string
import pandas as pd
from anytree import PreOrderIter
from build_tree import create_food_tree


with open('/Users/annalisaszymanski/Main1/FoodOptimization/python_functions/updated_word_dict_food_products.pkl', 'rb') as f:
    loaded_keywords_list = pickle.load(f)

def get_highest_scoring_matches(user_inputs, food_items):
    highest_matches = []
    filtering_word = []

    for user_input in user_inputs:
        matches = process.extract(user_input, food_items)
        highest_match = max(matches, key=lambda x: x[1])
        highest_matches.append(highest_match[0])  # Append only the keyword to the list

        # Clean and split the strings
        user_input_words = set(clean_and_split(user_input.lower()))
        match_words = set(clean_and_split(highest_match[0].lower()))

        candidate_filtered_word = user_input_words - match_words
        filtering_word.append([ x for x in candidate_filtered_word if x.lower() in loaded_keywords_list])

    return highest_matches, filtering_word

def get_highest_scoring_match(user_input, food_items):
    matches = process.extract(user_input, food_items, limit=1)
    highest_match = matches[0]
    return highest_match[0]

def clean_and_split(s):
    # Remove punctuation and split
    return s.translate(str.maketrans('', '', string.punctuation)).split()


root = create_food_tree('../updated_food_hierarchy2.csv')
nodes_list = [node.name for node in PreOrderIter(root)]
node_list2 = ["Breaded Chicken Tenderloins", "Bread, Rolls, Tortilla"]
# Test the function with multiple user inputs
user_inputs = ["Bread"]
# user_inputs = [
# "Pasta",
# "Eggs",
# "Cheese",
# "Yogurt",
# "Pasta",
# "Rice",
# "Bread",
# "All-purpose Flour",
# "Cereal",
# "Butter",
# "Soup",
# "Red Beans",
# "Tuna",
# "Dried Fruit",
# "Salt",
# "Pepper",
# "Basil",
# "Oregano",
# "Coriander",
# "Cumin",
# "Cooking Oil"]

# Fuzzy Matching of user input to hierarchy node (highest scoring match)
highest_matches, match_to_filter_df = get_highest_scoring_matches(
    user_inputs, node_list2)

print("Highest Matches:")
print(highest_matches)
print("------------------")
print("Filtered Words:")
print(match_to_filter_df)


# #If equal matching scores between nodes we will want to change the code to search within both nodes

# # Test the function with multiple user inputs
# user_inputs = ["Pasta"]
# food_items = [
# 'Linguine',
# 'Whole Grain Penne Pasta',
# 'Gluten-Free Pasta',
# 'Elbows Pasta',
# 'Rigatoni Pasta',
# 'Farfalle Pasta',
# 'Fideo Macaroni',
# 'Egg Noodles',
# 'Angel Hair Pasta', 
# 'Pasta, noodles, cooked grains'
# ]

# # Get the highest scoring matches for each user input
# highest_matches, filtere = get_highest_scoring_matches(user_inputs, food_items)

# print(highest_matches)

# #"Boneless Kroger Chicken Breast"
# #['Boneless', 'Kroger']
