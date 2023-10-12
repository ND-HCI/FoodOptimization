import pandas as pd

# Load product names file and convert to lowercase
product_names = pd.read_csv('output_of_keywords.csv')
product_names['description2'] = product_names['description2'].str.lower()

# Load Kroger data file and convert descriptions to lowercase
kroger_data = pd.read_csv('../walmart_products.csv')
kroger_data['Product Name'] = kroger_data['Product Name'].str.lower()

# Initialize match counter
match_counter = 0

# Loop through all descriptions in Kroger data
for description in kroger_data['Product Name'].values:
    # Check if any product name is within the current description
    for product in product_names['description2']:  # Assuming 'product' as column name in output_of_keywords.csv
        if product in description:
            match_counter += 1
            break  # Break the inner loop as soon as we find a match to avoid double-counting

total_descriptions = len(kroger_data)
percentage_matched = (match_counter / total_descriptions) * 100

print(f'There are {match_counter} matches out of {total_descriptions} descriptions in the Walmart dataset. ({percentage_matched}%)')
