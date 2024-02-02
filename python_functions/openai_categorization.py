import os
import openai
import pandas as pd
import time
from tqdm import tqdm
import csv
openai.api_key = "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"

def generate_category(text):
    while True: 
        try:
            completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                #few shot learning and in-context learning (we are showing the demonstrations in the context of the LLM)
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "I am going to provide you with a product name and would like you to pull out the keyword(s) for this product. We want the keywords to organize the products into categories.  The keywords should be indentified to group similar products together under the same keyword categorization."}, 
                {"role": "user", "content": "Tyson Tender & Juicy Extra Meaty Fresh Pork Baby Back Ribs"}, 
                {"role": "assistant", "content": "Pork Ribs"},
                {"role": "user", "content": "Honeysuckle White¬Æ 97% Fat Free Ground White Turkey Tray"}, 
                {"role": "assistant", "content": "Ground Turkey"},
                {"role": "user", "content": "SOUR PATCH KIDS and SWEDISH FISH Mini Soft & Chewy Candy Variety Pack"}, 
                {"role": "assistant", "content": "Candy Variety Pack"},
                {"role": "user", "content": "Funables Paw Patrol Movie Fruit Flavored Fruit Snacks"}, 
                {"role": "assistant", "content": "Fruit Snack"},
                {"role": "user", "content": "Hiland Whole Vitamin D Milk"}, 
                {"role": "assistant", "content": "Milk"},
                {"role": "user", "content": "Utz Potato Stix"}, 
                {"role": "assistant", "content": "Potato Snacks"},
                {"role": "user", "content": "Diet Coke Soda Pop, 12 fl oz, 24 Pack Cans"}, 
                {"role": "assistant", "content": "Soda"},
                {"role": "user", "content": "Heinz Tomato Ketchup, 32 oz Bottle"}, 
                {"role": "assistant", "content": "Ketchup"},
                {"role": "user", "content": "Health-Ade Probiotic Kombucha Tea, Pink Lady Apple, 16 fl oz"}, 
                {"role": "assistant", "content": "Kombucha"},
                {"role": "user", "content": "Great Value Hot Dog Buns, White, 11 oz, 8 Count"}, 
                {"role": "assistant", "content": "Hot Dog Buns"},
                {"role": "user", "content": text}

                
            ], 
            temperature = 0, 
            max_tokens = 10 #What is the most number of words you want it to generate 10 may be good
            )

            time.sleep(6)

            return completion.choices[0].message["content"]
        except Exception as e: 
            print(e)
            time.sleep(30)

df = pd.read_csv('../walmart_products_10-23-23_3.csv')
output_file_path = '../walmart_api_output5.csv'

if not os.path.exists(output_file_path):
    with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Walmart Item ID', 'Product Name', 'Category'])

# Open the file in append mode.
with open(output_file_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            item_id = row["Walmart Item ID"]
            name = row["Product Name"]
            category = generate_category(name)
            print(f"Processing {name}, ID {item_id}: Category {category}")
            writer.writerow([item_id, name, category])
            f.flush()  # Force flushing the buffer to the file
        except Exception as e:
            print(f"Failed to process row {idx}: {e}")

print("Finished processing.")

# output_file_path = '../walmart_api_output.csv'

# with open(output_file_path, 'a') as f:
#     for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
#         try:
#             item_id = row["Walmart Item ID"]
#             name = row["Product Name"]
#             category = generate_category(name)
#             print(name, ":", category)
#             # Write the row to the file
#             f.write(f'{item_id},{name},{category}\n')
#         except Exception as e:
#             print(f"Failed to process row {idx}: {e}")



# # df['Product Name'] = df['Product Name'].str.split(',', 1).str[0]
# output_df = pd.DataFrame(columns=["Walmart Item ID", "Product Name", "Category"])

# for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
#     try:
#         item_id = row["Walmart Item ID"]
#         name = row["Product Name"]
#         category = generate_category(name)
#         print(name, ":", category)
#         # Append the result to the output DataFrame
#         output_df = pd.concat(
#             [output_df, pd.DataFrame({"Walmart Item ID": [item_id], "Product Name": [name], "Category": [category]})],
#             ignore_index=True
#         )
#     except Exception as e:
#         print(f"Failed to process row {idx}: {e}")

# # Once the loop is finished, save the DataFrame to a CSV
# output_df.to_csv('../walmart_api_output2.csv', index=False)

# with open('../walmart_api_output2.csv', "w") as f:

#     for idx, row in tqdm(list(df.iterrows())[:200]):
#         name = row["Product Name"]
#         category = generate_category(name)
#         print(name, ":",  category)
#         f.write(f'{name},{category}\n')

#Save file
#retreival augmented generation
#What would happen if API goes down or if there is an error - error handling stops the program from crashing
#save each row you get it back 