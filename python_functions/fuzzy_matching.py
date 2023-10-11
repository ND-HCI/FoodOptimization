from fuzzywuzzy import process
import pandas as pd

#relevance models - BERT open source HuggingFace
#Bert understands language, has a lot of parameters but not as big as LLMs
#knowledge of the words that is further than direct matching of the strings
#word embedding (Word2vec) could be useful but may not be contextualized so would not take into account the neighboring words
#input of bert will be user input and output will be embedding for each word that would be contextualized

# User input
user_input = "cheder cheese crackers"

food_items = ["Cheddar Cheese", "Blue Cheese", "Goat Cheese", "Mozzarella Cheese", "Crackers"]

file_path = '../test+data/keywords.xlsx'
df = pd.read_excel(file_path, engine='openpyxl')
food_items = df['Keywords'].tolist()  # Assuming the column name containing keywords is 'Keywords'


matches = process.extract(user_input, food_items)

selected_matches = [match for match in matches if match[1] >= 80]  # 80 is the similarity score threshold

print(selected_matches)
