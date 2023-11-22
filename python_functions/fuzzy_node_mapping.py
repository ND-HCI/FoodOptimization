import pickle
from fuzzywuzzy import process
import string
import pandas as pd
from anytree import PreOrderIter

with open('word_dict_food_products.pkl', 'rb') as f:
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


# root = create_food_tree('../tree_mapping.csv')  
# leaf_nodes = [node.name for node in PreOrderIter(root) if not node.children]
# # Test the function with multiple user inputs
# user_inputs = ["Cheddar Cheese", "2% Milk", "Chocolate Milk", "Mozzarella Cheese", "2% Cheddar Cheese"]

# highest_matches, filtering_words = get_highest_scoring_matches(user_inputs, leaf_nodes)

# print("Highest Matches:", highest_matches)
# print("Filtering Words:", filtering_words)

#If equal matching scores between nodes we will want to change the code to search within both nodes

# # Test the function with multiple user inputs
# user_inputs = ["Cheese", "Cheddar Cheeese", "2% Milk", "Chocolate Milk", "Jerky", "Advocado Oil"]
# food_items = [
#     'Cheese', 
#     'Cheese, American',
#     'Cheese, Blue or Roquefort',
#     'Cheese, Brick',
#     'Cheese, Brie',
#     'Cheese, Camembert',
#     'Cheese, Cheddar',
#     'Cheese, Colby',
#     'Cheese, Colby Jack',
#     'Cheese, cottage',
#     'Cheese, Feta',
#     'Cheese, Fontina',
#     'Cheese, goat',
#     'Cheese, Gouda or Edam',
#     'Cheese, Gruyere',
#     'Cheese, Limburger',
#     'Cheese, Mexican blend',
#     'Cheese, Monterey',
#     'Cheese, Mozzarella',
#     'Cheese, Muenster',
#     'Cheese, paneer',
#     'Cheese, Parmesan',
#     'Cheese, Port du Salut',
#     'Cheese, Provolone',
#     'Cheese, Ricotta',
#     'Cheese, Swiss',
#     'Milks, milk drinks, yogurts, infant formulas', 
#     'Milk Varieties', 
#     'Non-dairy Milk', 
#     'Milk',
#     'Buttermilk',
#     'Goat’s Milk',
#     'Non-dairy Milk',
#     'Soy milk',
#     'Almond milk',
#     'Rice milk',
#     'Coconut milk',
#     'Flavored Milk & Drinks',
#     'Chocolate milk',
#     'Chocolate milk drink',
#     'Strawberry milk',
#     'Milk shake',
#     'Milk shake with malt', 
#     'Beef jerky',
#     'Pork',
#     'Pork jerky',
#     'Chicken Breast'
#     'Advocado',
#     'Advocado Dressing'
# ]

# # Get the highest scoring matches for each user input
# highest_matches = get_highest_scoring_matches(user_inputs, food_items)

# print(highest_matches)

# #"Boneless Kroger Chicken Breast"
# #['Boneless', 'Kroger']
