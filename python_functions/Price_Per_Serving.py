import os
import openai
import pandas as pd
import time
from tqdm import tqdm
import csv
openai.api_key = "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"

def generate_number_of_servings(text, max_retries=3):
    retries = 0
    while retries < max_retries: 
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[ 
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": "You will be given a food category description.  For each description, estimate the serving size for a product based on standard guidelines.  For example the standard serving size for meat is 4 oz and for vegetables is 1 cup.  Please estimate this for each category provided. The output should be {number} {unit}. The output should be in oz, fl oz, g, ml, tsp, tbsp, cup, or lb. RETURN ONLY A NUMBER AND THE UNIT, NO OTHER TEXT."},
                    {"role": "user", "content": "Pork Ribs"}, 
                    {"role": "assistant", "content": "4 oz"},
                    {"role": "user", "content": "Ketchup"}, 
                    {"role": "assistant", "content": "1 tbsp"},
                    {"role": "user", "content": "Chicken Drumsticks"}, 
                    {"role": "assistant", "content": "4 oz"},

                    # {"role": "user", "content": "The product description and product size will be provided for each product.  With this information, I would like to return the estimated serving size based on standard guidelines and the number of servings for each product. Then, to produce the number of servings divide the product size/estimated serving size. Sometimes the product size can be found in the product description. If the product size is blank or cannot be assumed, do not calculate the NOS. The output should look like this 'Serving Size: 4 oz, NOS: 12. If the output cannot be determined just put N/A, do not provide additional text.'"},
                    # {"role": "user", "content": "Description: Tyson Tender & Juicy Extra Meaty Fresh Pork Baby Back Ribs, 2.9 - 4.0 lb Serving Size: Product Size: 48 oz/3 lbs"}, 
                    # {"role": "assistant", "content": "Serving Size: 4 oz, NOS: 12"},
                    # # {"role": "user", "content": "Description: Great Value Large White Eggs, 12 Count Serving Size: Product Size: "}, 
                    # # {"role": "assistant", "content": "Serving Size: 1, NOS: 12"},
                    # # {"role": "user", "content": "Description:  Health-Ade Probiotic Kombucha Tea, Pink Lady Apple, 16 fl oz	Serving Size: 237ml	Product Size: 16 fl oz/473 mL/1 PT "}, 
                    # # {"role": "assistant", "content": "1.99"},
                    {"role": "user", "content": text}                
                    ],
                temperature=0, 
                max_tokens=15
            )
            return completion.choices[0].message["content"]
        except Exception as e: 
            print(f"Error: {e}. Retrying... ({retries+1}/{max_retries})")
            retries += 1
            time.sleep(10)  # Adjusted sleep time
    return "Error: Unable to process"

# Load DataFrame
df = pd.read_csv('../randomwalmartstuff.csv')
unique_values = df['Category'].unique()
unique_list = unique_values.tolist()
# df = df[df['Extracted Count'].isnull()]
output_file_path = '../walmart_serving_sizes6.csv'

# Processed UPC codes
processed_upc_codes = set()
if os.path.exists(output_file_path):
    with open(output_file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader, None)  # Skip header
        for row in reader:
            if row:  # Check if row is not empty
                processed_upc_codes.add(row[0])

with open(output_file_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    if not processed_upc_codes:
        writer.writerow(['Category', 'Estimated Serving Size'])

    # Iterate through the unique_list instead of unique_values DataFrame
    for category in tqdm(unique_list, total=len(unique_list)):
        if category in processed_upc_codes:
            continue  # Skip already processed items

        try:
            name = category  # Just use the category directly
            servings = generate_number_of_servings(name)
            print(servings)
            writer.writerow([name, servings])
            f.flush()  # Ensure data is written to file
        except Exception as e:
            print(f"Failed to process category {category}: {e}")

    print("Finished processing.")


# # Processed UPC codes
# processed_upc_codes = set()
# if os.path.exists(output_file_path):
#     with open(output_file_path, 'r', encoding='utf-8') as f:
#         reader = csv.reader(f)
#         next(reader, None)  # Skip header
#         for row in reader:
#             if row:  # Check if row is not empty
#                 processed_upc_codes.add(row[0])

# with open(output_file_path, 'a', newline='', encoding='utf-8') as f:
#     writer = csv.writer(f)
#     if not processed_upc_codes:
#         writer.writerow(['Category', 'Estimated Serving Size'])

#     for idx, row in tqdm(unique_values.iterrows(), total=unique_values.shape[0]):
#         item_id = row["Category"]
#         if item_id in processed_upc_codes:
#             continue  # Skip already processed items

#         try:
#             name = row["Category"]
#             # full_serving_size = str(row['Serving Size']) + ' ' + str(row['Serving Size Unit'])
#             # data = 'Description: ' + name + ' Product Size: ' + str(row['Extracted Size'])
#             # data = 'Description: ' + name + ' Serving Size: ' + full_serving_size + ' Product Size: ' + str(row['Product Size'])
#             servings = generate_number_of_servings(name)
#             print(servings)
#             writer.writerow([name, servings])
#             f.flush() # Ensure data is written to file
#         except Exception as e:
#             print(f"Failed to process row {idx}: {e}")

#     print("Finished processing.")




