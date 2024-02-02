import pandas as pd
from transformers import BertTokenizer, BertModel
from build_tree import create_food_tree
from anytree import PreOrderIter
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

# user_input = "Cheddar cheese crackers"

food_items = [
"Bread"]

food_products = ["Bread, Rolls, Tortillas", "Breaded Chicken Tenderloins", "White Bread", "Yeast Breads"]

#Split the strings with commas into individual words
#Test splitting the string by comma and matching to those individual words

#Constrain the string matching to get around challenges that it has
#Breads, Wraps, or Rolls

# # Load data from Excel file into a DataFrame
# excel_file = '../test_data/keywords.xlsx'
# df = pd.read_excel(excel_file, engine='openpyxl')
# # Convert the DataFrame into a list
# food_items = df['short_description'].tolist()

# # Load data from CSV file into a DataFrame
# csv_file = '../database_cleaned_fullgrocery_with_parents.csv'
# df = pd.read_csv(csv_file)

# # Convert the DataFrame into a list using the "Descriptions" column
# food_products= df['Description'].tolist()

# root = create_food_tree('../updated_food_hierarchy2.csv')
# food_products = [node.name for node in PreOrderIter(root)]

def embed(text):
    encoded_input = tokenizer(text, return_tensors='pt')
    output = model(**encoded_input)
    embeddings = output.last_hidden_state[0].mean(dim=0)  # Take the average across sequence length dimension
    return embeddings  # Gives us a vector per word

# Generate embeddings for each food item and food product
food_embeddings = [embed(item) for item in food_items]
product_embeddings = [embed(item) for item in food_products]

def score(e1, e2):
    # Euclidean distance or cosine distance or similarity 
    dist = (e1 - e2)**2
    sum_dist = dist.sum()  # Could also take mean too if number is too big
    return -sum_dist

# For each food item, find the food product with the highest score (i.e., smallest distance)
best_matches = []
for item, item_embedding in zip(food_items, food_embeddings):
    # Compute scores for this item against all products
    scores = [(product, score(item_embedding, prod_embedding).item()) for product, prod_embedding in zip(food_products, product_embeddings)]
    scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score in descending order (because we use negative distance as score)
    best_match = scores[0]  # The top score is the best match
    best_matches.append((item, best_match[0], best_match[1]))  # Save the item, the best matching product, and the score

# Print or process the best matches
for item, best_match, score in best_matches:
    print(f"Item: {item}, Best Match: {best_match}, Score: {score}")
