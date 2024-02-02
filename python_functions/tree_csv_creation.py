import pandas as pd

# Load the hierarchy and products data
hierarchy = pd.read_csv('../food_hierarchy_wweia.csv')
products = pd.read_csv('keyword_wweiacode_data.csv')

# This will keep track of the next ID to assign to a new node
next_id = hierarchy['ID'].max() + 1

# A function to find the Parent_ID for a given category
def find_parent_id(category):
    parent = hierarchy[hierarchy['Value'] == category]
    if not parent.empty:
        return parent.iloc[0]['ID']
    else:
        return None

# Loop through the classified products and add them to the hierarchy
for _, row in products.iterrows():
    parent_id = find_parent_id(row['wweia_food_category_description'])
    if parent_id is not None:
        # Append new row to the hierarchy
        hierarchy = hierarchy.append({'ID': next_id, 'Parent_ID': parent_id, 'Value': row['Keyword']}, ignore_index=True)
        next_id += 1

# Save the updated hierarchy to a new CSV file
hierarchy.to_csv('../updated_food_hierarchy2.csv', index=False)