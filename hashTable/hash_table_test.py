import csv

# Create an empty dictionary to act as the hash table
product_hash_table = {}

# Open the csv file
with open('../fdc_kroger_combined_per_serving.csv', 'r') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header row
    for row in reader:
        # Split product name into keywords
        keywords = row[2].lower().split()  # Assuming product name is in the first column
        for keyword in keywords:
            # If keyword is already in the hash table, append the product
            # If keyword is not in the hash table, add it with a new list containing the product
            product_hash_table.setdefault(keyword, []).append(row[2])

keyword = "ray's"

# Check if the keyword is in the hash table
if keyword in product_hash_table:
    # Get the list of products associated with the keyword
    products = product_hash_table[keyword]
    print(f"Products associated with '{keyword}': {products}")
else:
    print(f"No products associated with '{keyword}'")
