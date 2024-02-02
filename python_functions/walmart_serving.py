import pandas as pd
import numpy as np
import re

def extract_count(product_name):
    """
    Extracts the count or number of pieces/cans from the product name.

    Args:
    product_name (str): The name of the product.

    Returns:
    int or None: The extracted count if found, otherwise None.
    """
    # Define a regular expression pattern to find numbers followed by relevant keywords
    pattern = r'(\d+)\s*(count|pieces|cans|pack|pcs|ct)'
    
    # Search for the pattern in the product name
    match = re.search(pattern, product_name, re.IGNORECASE)
    
    if match:
        # Return the numerical part of the match as an integer
        return int(match.group(1))
    else:
        # Return None if no match is found
        return None
    
def extract_size(product_name):
    """
    Extracts the size of the product from the product name.

    Args:
    product_name (str): The name of the product.

    Returns:
    str or None: The extracted size if found, otherwise None.
    """
    # Define a regular expression pattern to find size patterns
    pattern = r'(\d+\.?\d*\s*(lbs|lb|oz|fl oz|fl. Oz|g|kg|ml|l|L|Pint))'
    
    # Search for the pattern in the product name
    match = re.search(pattern, product_name, re.IGNORECASE)
    
    if match:
        # Return the matched size pattern
        return match.group(1)
    else:
        # Return None if no match is found
        return None
    
def convert_units(amount, from_unit, to_unit):
    """
    Convert between units if necessary
    """
    if from_unit == to_unit:
        return amount
    if pd.isnull(from_unit) or pd.isnull(to_unit):
        return None  # Can't convert if one of the units is NaN
    try:
        return amount * conversion_rates[from_unit][to_unit]
    except KeyError:
        raise ValueError(f"Conversion from {from_unit} to {to_unit} not available")


def calculate_servings(row):
    """
    Calculate the number of servings per product.
    """
    # If Extracted Count is available, use it directly
    if pd.notnull(row['Extracted Count']):
        return row['Extracted Count']
    
    # If Extracted Size is available, calculate based on it
    if pd.notnull(row['Extracted Size']):
        match = re.match(r'(\d+\.?\d*)\s*(\w+)', str(row['Extracted Size']))
        if match:
            size_value, size_unit = match.groups()
            size_value = float(size_value)

            serving_size_unit = str(row['Serving Size Unit']).lower() if pd.notnull(row['Serving Size Unit']) else None
            
            try:
                # Convert the serving size to the unit of the extracted size if necessary
                converted_serving_size = convert_units(row['Serving Size'], serving_size_unit, size_unit.lower())
                # Calculate the number of servings
                if converted_serving_size is not None:
                    return size_value / converted_serving_size
            except ValueError:
                # Return None if conversion is not available
                return None

    # Return None if the number of servings cannot be calculated
    return None

# Define the conversion rates (as an example)
conversion_rates = {
    'oz': {'g': 28.3495, 'lb': 0.0625, 'fl oz': 1},  # 'oz' is equivalent to 'fl oz' for fluids
    'g': {'oz': 0.035274, 'lb': 0.00220462},
    'ml': {'fl oz': 0.033814, 'fl': 0.033814, 'oz': 0.033814}, # Correct conversion for ml to oz (assuming fluid ounces)
    'lb': {'oz': 16, 'g': 453.592},
    'fl oz': {'ml': 29.5735, 'oz': 1}, # Assuming 'oz' here means 'fl oz'
   }

# Load the CSV file
file_path = '../updated_11-20-23_walmart_products.csv'
df = pd.read_csv(file_path, dtype={2: str})

est_serving = pd.read_csv('../walmart_serving_sizes6.csv')

# Drop duplicate entries based on 'Category', keeping the first instance
est_serving = est_serving.drop_duplicates(subset=['Category'], keep='first')

# Merge the two dataframes on the 'Category' column
merged_df = pd.merge(df, est_serving, on='Category', how='left')

# Apply the function to the 'Product Name' column
merged_df['Extracted Count'] = merged_df['Product Name'].apply(extract_count)

# Apply the function to the 'Product Name' column
merged_df['Extracted Size'] = merged_df['Product Name'].apply(extract_size)

# Apply the function to each row in the DataFrame
merged_df['Number of Servings'] = merged_df.apply(calculate_servings, axis=1)

# Display the first few rows of the dataframe to see the results
merged_df.to_csv('../randomwalmartstuff.csv', index=False)
