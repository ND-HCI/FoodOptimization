#put the walmart product image in the merged_walmart file
import pandas as pd

def merge_walmart_data(merged_file, products_file):
    # Read the CSV files into dataframes
    merged_df = pd.read_csv(merged_file)
    products_df = pd.read_csv(products_file)

    # Merge the dataframes on the 'UPC Code' column
    merged_data = pd.merge(merged_df, products_df[['UPC Code', 'Image URL']], on='UPC Code', how='left')

    return merged_data

# Use the function
merged_data = merge_walmart_data('../../merged_walmart_data.csv', '../../walmart_products_11-20-23.csv')

# Optionally, save the merged data to a new CSV file
merged_data.to_csv('../../merged_walmart_data_with_images.csv', index=False)

