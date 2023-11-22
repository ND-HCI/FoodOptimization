from fuzzywuzzy import process, fuzz
import pandas as pd

#relevance models - BERT open source HuggingFace
#Bert understands language, has a lot of parameters but not as big as LLMs
#knowledge of the words that is further than direct matching of the strings
#word embedding (Word2vec) could be useful but may not be contextualized so would not take into account the neighboring words
#input of bert will be user input and output will be embedding for each word that would be contextualized

# Simple ratio comparison
ratio = fuzz.ratio("Kroger¬Æ Low Fat Ricotta Cheese", "Cheese, Ricotta")
print(ratio)  # Outputs a score showing similarity

# Partial ratio
partial_ratio = fuzz.partial_ratio("Kroger¬Æ Low Fat Ricotta Cheese", "Cheese, Ricotta")
print(partial_ratio)

# Token sort ratio
sort_ratio = fuzz.token_sort_ratio("Kroger¬Æ Low Fat Ricotta Cheese", "Cheese, Ricotta")
print(sort_ratio)

# Token set ratio
set_ratio = fuzz.token_set_ratio("Kroger¬Æ Low Fat Ricotta Cheese", "Cheese, Ricotta")
print(set_ratio)



# User input
food_items = ['Protein', 'Milk, reduced fat (2%)', 'Milk, whole', 'Milk, low fat (1%)', 'Milk, evaporated, whole', 'Milk, fat free (skim)', 'Milk, condensed, sweetened', 'Milk, malted', 'Buttermilk', 'Goat’s Milk', 'Lactose-free reduced fat', 'Lactose-free whole milk', 'Lactose-free skim milk', 'Lactose-free fat free (skim)', 'Soy milk', 'Almond milk, sweetened', 'Almond milk, sweetened, chocolate', 'Almond milk, unsweetened', 'Almond milk, unsweetened, chocolate', 'Rice milk', 'Coconut milk', 'Oat milk, unsweetened', 'Oat milk, sweetened', 'Hemp milk, unsweetened', 'Hemp milk, sweetened', 'Chocolate milk', 'Hot chocolate / Cocoa', 'Strawberry milk', 'Eggnog', 'Yogurt, whole milk, plain', 'Yogurt, low fat milk, plain', 'Yogurt, nonfat milk, plain', 'Yogurt, liquid', 'Yogurt, coconut milk', 'Yogurt, Greek', 'Yogurt, soy', 'Chipotle dip', 'Onion dip', 'Ranch dip', 'Spinach dip', 'Tzatziki dip', 'Vegetable dip', 'Sour Cream', 'Cream', 'Half & Half', 'Almond Milk Creamer', 'Soy Milk Creamer', 'Coffee Creamer Powder', 'Frozen Yogurt', 'Frozen yogurt sandwich', 'Frozen yogurt bar', 'Frozen yogurt cone', 'Ice cream', 'Gelato', 'Ice cream bar', 'Ice cream candy bar', 'Ice cream sandwich', 'Ice cream cone', 'Ice cream sundae', 'Banana split', 'Soft serve', 'Sherbet', 'Creamsicle', 'Fudgesicle', 'Ice cream soda', 'Pudding', 'Custard', 'Flan', 'Creme brulee', 'Firni', 'Banana pudding', 'Mousse', 'Dulce de leche', 'Barfi or Burfi', 'Trifle', 'Tiramisu', 'Whipped Cream', 'Artichoke dip', 'Seafood dip', 'Cheese dip', 'Cheese fondue', 'Cheese sauce', 'Alfredo Sauce', 'Cream Cheese', 'Cream cheese spread', 'Cheese spread', 'Cheese ball', 'Imitation cheese', 'Cheese, Blue or Roquefort', 'Cheese, Brick', 'Cheese, Camembert', 'Cheese, Brie', 'Cheese, Cheddar', 'Cheese, Colby', 'Cheese, Feta', 'Cheese, Fontina', 'Cheese, goat', 'Cheese, Gouda or Edam', 'Cheese, Gruyere', 'Cheese, Limburger', 'Cheese, Monterey', 'Cheese, Mozzarella', 'Cheese, Muenster', 'Cheese, Parmesan', 'Cheese, Port du Salut', 'Cheese, Provolone', 'Cheese, Swiss', 'Cheese, paneer', 'Cheese, Mexican blend', 'Cheese, American', 'Cheese, Ricotta', 'Cheese, cottage', 'Queso Anejo', 'Queso Asadero', 'Queso Fresco', 'Queso cotija', 'Vegetable', 'Fruit', 'Grain', 'Other']

user_inputs = [
'Daisy Low Fat Cottage Cheese']
# # Load data from Excel file into a DataFrame
# excel_file = '../test_data/keywords.xlsx'
# df = pd.read_excel(excel_file, engine='openpyxl')
# # Convert the DataFrame into a list
# food_items = df['short_description'].tolist()

all_matches = []
for user_input in user_inputs:
    # Use token_set_ratio as the scorer
    matches = process.extract(user_input, food_items, scorer=fuzz.token_set_ratio)
    print(matches)
    # Filter matches based on a threshold
    selected_matches = [match for match in matches if match[1] >= 80]
    all_matches.extend(selected_matches)

print(all_matches)


# all_matches = []
# for user_input in user_inputs:
#     matches = process.extract(user_input, food_items)
#     print(matches)
#     # Filter matches based on a threshold, e.g., 80
#     selected_matches = [match for match in matches if match[1] >= 50]
#     all_matches.extend(selected_matches)

# print(all_matches)

