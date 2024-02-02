import os
import openai
import pandas as pd
import time
from tqdm import tqdm
import csv
openai.api_key = "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"

def generate_category(text, category_string):
    while True: 
        try:
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    #few shot learning and in-context learning (we are showing the demonstrations in the context of the LLM)
                    {"role": "system", "content": "Here is the list of WWEIA categories:\n" + category_string},
                    {"role": "user", "content": "Please assist in categorizing products under the 'What We Eat in America' (WWEIA) framework. Here's how it works:  1). You will receive the name of a product.  2) Extract keywords from the product name to form 'subcategories'. The keywords should be identified to group similar products together under the same keyword categorization. 3) Next, classify each identified subcategory into the most appropriate category from the provided list of WWEIA categories.  Remember, these keywords will function as subcategories under the broader WEEIA categories. The output format should be 'keyword : category"}, 
                    {"role": "user", "content": "Tyson Tender & Juicy Extra Meaty Fresh Pork Baby Back Ribs"}, 
                    {"role": "assistant", "content": "Pork Ribs: Pork"},
                    {"role": "user", "content": "Oscar Mayer Deli Fresh Rotisserie Seasoned Chicken Breast, for a Low Carb Lifestyle, 9 oz Tray"}, 
                    {"role": "assistant", "content": "Deli Chicken Breast: Deli and cured meat sandwiches"},
                    {"role": "user", "content": "Great Value All Natural Chicken Breast Tenderloins, 3 lb (Frozen)"}, 
                    {"role": "assistant", "content": "Chicken Breast: Chicken, whole pieces"},
                    {"role": "user", "content": "Honeysuckle White¬Æ 97% Fat Free Ground White Turkey Tray"}, 
                    {"role": "assistant", "content": "Ground Turkey: Turkey, duck, other poultry"},
                    {"role": "user", "content": "SOUR PATCH KIDS and SWEDISH FISH Mini Soft & Chewy Candy Variety Pack"}, 
                    {"role": "assistant", "content": "Candy Variety Pack: Candy not containing chocolate"},
                    {"role": "user", "content": "Funables Paw Patrol Movie Fruit Flavored Fruit Snacks"}, 
                    {"role": "assistant", "content": "Fruit Snack: Nutrition bars"},
                    {"role": "user", "content": "Hiland Whole Vitamin D Milk"}, 
                    {"role": "assistant", "content": "Vitamin D Milk: Milk, whole"},
                    {"role": "user", "content": "Utz Potato Stix"}, 
                    {"role": "assistant", "content": "Potato Stix: Pretzels/snack mix "},
                    {"role": "user", "content": "Diet Coke Soda Pop, 12 fl oz, 24 Pack Cans"}, 
                    {"role": "assistant", "content": "Diet Soda: Diet soft drinks"},
                    {"role": "user", "content": "Sprite Lemon Lime Soda Pop, 12 fl oz, 24 Pack Cans"}, 
                    {"role": "assistant", "content": "Sprite: Soft drinks"},
                    {"role": "user", "content": "Birds Eye Steamfresh Roasted Red Potato Blend, Frozen, 10 oz"}, 
                    {"role": "assistant", "content": "Frozen Potato Blend: Other vegetables and combinations"},
                    {"role": "user", "content": "Heinz Tomato Ketchup, 32 oz Bottle"}, 
                    {"role": "assistant", "content": "Ketchup: Tomato-based condiments"},
                    {"role": "user", "content": "Health-Ade Probiotic Kombucha Tea, Pink Lady Apple, 16 fl oz"}, 
                    {"role": "assistant", "content": "Kombucha: Tea"},
                    {"role": "user", "content": "Great Value Hot Dog Buns, White, 11 oz, 8 Count"}, 
                    {"role": "assistant", "content": "Hot Dog Buns: Rolls and buns"},
                    {"role": "user", "content": "Processing Great Value 2% Reduced Fat Milk, 128 Fl Oz"}, 
                    {"role": "assistant", "content": "2% Milk: Milk, reduced fat"},
                    {"role": "user", "content": "Great Value 1% Low Fat Chocolate Milk, Half Gallon, 64 fl oz"}, 
                    {"role": "assistant", "content": "1% Chocolate Milk: Flavored milk, lowfat"},
                    {"role": "user", "content": text}
                ], 
            temperature = 0, 
            max_tokens = 30 #What is the most number of words you want it to generate 10 may be good
            )

            time.sleep(3)

            return completion.choices[0].message["content"]
        
        except Exception as e: 
            print(e)
            time.sleep(30)

wweia = 'wweia_food_category.csv'
wweia_df = pd.read_csv(wweia)
category_list = wweia_df['wweia_food_category_description'].tolist()
category_string = "\n".join(category_list)
dtype_spec = {2: str, 3: str}
df = pd.read_csv('../walmart_products_11-20-23.csv', dtype=dtype_spec)
output_file_path = '../walmart_api_output7.csv'

def read_existing_ids(file_path):
    existing_ids = set()
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip head
            for row in reader:
                if row:  # Check if row is not empty
                    existing_id = row[0]  # Assuming Walmart Item ID is in the first column and stripping whitespace
                    existing_ids.add(existing_id)
    return existing_ids

# Read existing IDs
existing_ids = read_existing_ids(output_file_path)
print("Some existing IDs:", list(existing_ids))


# Create or append to the output file
with open(output_file_path, 'a', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)

    if not existing_ids:  # If the file was just created, write the header
        writer.writerow(['Walmart Item ID', 'Product Name', 'Keyword', 'Category'])

    for idx, row in tqdm(df.iterrows(), total=df.shape[0]):
        try:
            item_id = str(row["Walmart Item ID"])  # Convert to string and strip whitespace

            # Debug: Print the current item ID and check if it's in existing IDs
            print(f"Current ID: {item_id}, Already processed: {item_id in existing_ids}")

            if item_id in existing_ids:
                continue  # Skip this row if the ID is already processed
            
            print(f"Processing: {item_id}")
            name = row["Product Name"]
            output = generate_category(name, category_string)
            keyword, category = output.split(":", 1)
            print(f"Processing {name}, ID {item_id}: Keyword '{keyword}', Category '{category}'")
            writer.writerow([item_id, name, keyword, category])
            existing_ids.add(item_id)  # Add the new item ID to the set
            f.flush()  # Force flushing the buffer to the file
        except Exception as e:
            print(f"Failed to process row {idx}: {e}")


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