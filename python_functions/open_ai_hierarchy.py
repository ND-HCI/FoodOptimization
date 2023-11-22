import os
import openai
import pandas as pd
from tqdm import tqdm

# Set the OpenAI API key from an environment variable for better security practices.
openai.api_key = "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"

def get_completion_from_message(messages):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=0.0,
        )
        return response.choices[0].message["content"]
    except openai.error.OpenAIError as e:
        print(f"An error occurred: {e}")
        return None  # You can decide to return None or handle it differently

# Read categories from CSV file
wweia = '../FNDDS_Code_Data/wweia_food_category.csv'
wweia_df = pd.read_csv(wweia)
category_list = wweia_df['wweia_food_category_description'].tolist()
category_string = "\n".join(category_list)

# Define the system message just once, outside the loop
system_message = f"""You will be provided with food product keywords. Classify each keyword into the most relevant category from the following list:
{category_string}
"""

#Read Walmart File:
walmart_df = pd.read_csv('../walmart_10_23_keywords.csv')
unique_categories = walmart_df['Category'].unique()

# List to store results
results = []

# Iterate over each unique category
for product_name in tqdm(unique_categories):
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': product_name},
    ]

    category = get_completion_from_message(messages)
    results.append({"Product Name": product_name, "Predicted Category": category})
    print(f"Walmart Keyword: {product_name}\nPredicted category: {category}")

# Convert the results to a DataFrame and save it as a CSV file
results_df = pd.DataFrame(results)
results_df.to_csv('../classified_products.csv', index=False)
