import pandas as pd
from transformers import BertTokenizer, BertModel
model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)

model = BertModel.from_pretrained(model_name)

user_input = "Cheddar cheese crackers"

# food_items = ["Cheddar Cheese", "Blue Cheese", "Goat Cheese", "Mozzarella Cheese", "Crackers"]

# Load data from Excel file into a DataFrame
excel_file = '../test_data/keywords.xlsx'
df = pd.read_excel(excel_file, engine='openpyxl')
# Convert the DataFrame into a list
food_items = df['short_description'].tolist()

# Load data from CSV file into a DataFrame
csv_file = '../database_cleaned_fullgrocery_with_parents.csv'
df = pd.read_csv(csv_file)

# Convert the DataFrame into a list using the "Descriptions" column
food_products= df['Description'].tolist()


def embed(text):

    encoded_input = tokenizer(text, return_tensors='pt')

    output = model(**encoded_input)
    
    #shape 1, sequence_length, model_size
    embeddings = output.last_hidden_state[0].mean(dim=0) #take the average across sequence length dimention 
    #shape = model size, single vector that represents sequence
    return embeddings  #gives us a vector per word

food_embeddings = [embed(item) for item in food_items]
product_embeddings = [embed(item) for item in food_products]

#you can also save the food_embeddings save somewhere and we can load them

user_embedding = embed(user_input)
#bert score could compare the each vector or computing distance of every pair
def score(e1, e2):
    #euclidian distance or cosine distance or similarity 
    dist = (e1 - e2)**2
    sum_dist = dist.sum()  #could also take mean too if number is too big
    return -sum_dist

#now compute how close the two embeddings are, score/distance between user embedding and food item
food_scores = [(item, score(user_embedding, embedding).item()) for item, embedding in zip(food_products, product_embeddings)]

food_scores.sort(key=lambda x:x[1], reverse=True)

print(food_scores)