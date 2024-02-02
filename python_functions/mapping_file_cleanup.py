import pandas as pd

def clean_and_merge_data(walmart_file, wweia_file):
    # Load the Walmart data
    walmart_data = pd.read_csv(walmart_file)

    # Remove duplicate Walmart Item IDs, keeping the first occurrence
    walmart_data_unique = walmart_data.drop_duplicates(subset='Walmart Item ID', keep='first')

    # Load the WWEIA data
    wweia_data = pd.read_csv(wweia_file)

    walmart_data_unique['Category'] = walmart_data_unique['Category'].str.strip()
    wweia_data['wweia_food_category_description'] = wweia_data['wweia_food_category_description'].str.strip()

    # Merging the Walmart data with WWEIA data on the Category and WWEIA description
    merged_data = walmart_data_unique.merge(wweia_data, 
                                            left_on='Category', 
                                            right_on='wweia_food_category_description',
                                            how='left')
    
    print(merged_data)

    # Rename columns
    merged_data.rename(columns={'wweia_food_category': 'WWEIACode'}, inplace=True)

    # Create a dataframe for unique keyword to WWEIACode and description matchup
    keyword_wweiacode = merged_data[['Keyword', 'WWEIACode', 'wweia_food_category_description']].drop_duplicates()

    # Ensure unique keywords
    keyword_wweiacode = keyword_wweiacode.drop_duplicates(subset='Keyword', keep='first')

    # Remove rows with blank WWEIACode
    keyword_wweiacode = keyword_wweiacode[keyword_wweiacode['WWEIACode'].notna()]

    keyword_wweiacode.drop(columns=['WWEIACode'], inplace=True)

    # Save the keyword-WWEIACode-description data
    keyword_wweiacode.to_csv('keyword_wweiacode_data.csv', index=False)

    # Now you can safely drop the 'wweia_food_category_description' from merged_data
    merged_data.drop(columns=['wweia_food_category_description'], inplace=True)
    merged_data.drop(columns=['WWEIACode'], inplace=True)

    # Save the merged data
    merged_data.to_csv('updated_walmart_datayay.csv', index=False)

    return "Data cleanup and merging completed."

def add_category_to_walmart_products(walmart_products_file, walmart_file):
    # Load the Walmart products data
    walmart_products_data = pd.read_csv(walmart_products_file)
    
    # Remove duplicate Walmart Item IDs, keeping the first occurrence
    walmart_products_data_unique = walmart_products_data.drop_duplicates(subset='Walmart Item ID', keep='first')

    # Load the Walmart data and ensure it has unique Walmart Item IDs
    walmart_data = pd.read_csv(walmart_file)
    walmart_data_unique = walmart_data.drop_duplicates(subset='Walmart Item ID', keep='first')

    # Merge the unique Walmart products data with the unique Walmart data on Walmart Item ID
    merged_data = walmart_products_data_unique.merge(walmart_data_unique[['Walmart Item ID', 'Keyword']], 
                                                     on='Walmart Item ID', 
                                                     how='left')

    # Rename 'Keyword' column to 'Category'
    merged_data.rename(columns={'Keyword': 'Category'}, inplace=True)

    # Save the updated Walmart products data
    merged_data.to_csv('../updated_11-20-23_walmart_products.csv', index=False)

    return "Category added to Walmart products data."

# Example usage of the function
walmart_file = '../walmart_api_output7.csv'
walmart_products_file = '../walmart_products_11-20-23.csv'
wweia_file = 'wweia_food_category.csv'
# print(clean_and_merge_data(walmart_file, wweia_file))
print(add_category_to_walmart_products(walmart_products_file, walmart_file))
