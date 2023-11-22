import pandas as pd

# Load the data from the CSV files
walmart_api_df = pd.read_csv('../walmart_api_output4.csv')
walmart_product_df = pd.read_csv('../walmart_products_10-23-23_3.csv')

# Clean and prepare the data
# Ensure the ID columns are of the same type (string recommended)
walmart_api_df['Walmart Item ID'] = walmart_api_df['Walmart Item ID'].astype(str)
walmart_product_df['Walmart Item ID'] = walmart_product_df['Walmart Item ID'].astype(str)

# Remove duplicates in walmart_api_df based on 'Walmart Item ID'
walmart_api_df = walmart_api_df.drop_duplicates(subset='Walmart Item ID', keep='first')

# Merge the dataframes
# Assuming 'Walmart Product ID' in walmart_product_df corresponds to 'Walmart Item ID' in walmart_api_df
merged_df = walmart_product_df.merge(walmart_api_df[['Walmart Item ID', 'Category']], 
                                     left_on='Walmart Item ID', 
                                     right_on='Walmart Item ID', 
                                     how='left')

# Drop the extra 'Walmart Item ID' column from the merged dataframe
merged_df.drop('Walmart Item ID', axis=1, inplace=True)

# Save the updated dataframe to a new CSV file
merged_df.to_csv('merged_walmart_data.csv', index=False)

print("Merge completed and saved to 'merged_walmart_data.csv'")
