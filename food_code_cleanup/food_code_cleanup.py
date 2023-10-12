import pandas as pd
import numpy as np
import csv 

df = pd.read_csv('../fdc_kroger_combined_per_serving.csv')
kroger = pd.read_csv('../kroger_foodcode_output.csv')
unique = pd.read_csv('../python_functions/unique_values.csv')
FNDDS = pd.read_csv('../hashTable/mergedFNDDS.csv')

# Select only 'FDC_Description' and 'New' columns from the kroger dataframe
kroger = kroger[['FDC_Description', 'Food_Code', 'New']]

result = pd.concat([df, kroger], axis=1)

result['New'] = result['New'].str.rstrip()
unique['lower_short_description'] = unique['lower_short_description'].str.rstrip()

# Ensure both 'New' in result and 'lower_short_description' in unique are strings
result['New'] = result['New'].astype(str)
unique['lower_short_description'] = unique['lower_short_description'].astype(str)

# Make sure the keywords in both dataframes are lowercase for matching
result['New'] = result['New'].str.lower()
unique['lower_short_description'] = unique['lower_short_description'].str.lower()

# Merge the dataframes on the keywords
merged = pd.merge(result, unique, how='left', left_on='New', right_on='lower_short_description')

# Create a new column 'Flag' where 'New' is not 'nan' and 'lower_short_description' is null
merged['Flag'] = np.where((merged['New'] != 'nan') & (merged['lower_short_description'].isnull()), 1, 0)

merged.rename(columns={'food_code': 'food_code_replace'}, inplace=True)

FNDDS.rename(columns={'food_code': 'food_code_replace2'}, inplace=True)


# Convert 'Food_Code' in merged to string
merged['food_code_replace'] = merged['food_code_replace'].fillna(0).astype('int64')
FNDDS['food_code_replace2'] = FNDDS['food_code_replace2'].fillna(0).astype('int64')


# Merge the FNDDS dataframe with the merged dataframe
merged = pd.merge(merged, FNDDS, how='left', left_on='food_code_replace', right_on='food_code_replace2')

columns_to_drop = ['fdc_id_y', 'short_description',  'food_code_replace2', 'wweia_food_category', 'wweia_food_category_description']
merged = merged.drop(columns_to_drop, axis=1)

merged.to_csv('../combinedrandom.csv', index=False)

# Drop the rows where 'Flag' is 1
merged = merged[merged['Flag'] != 1]

# Replace 'Food_Code' with 'food_code_replace' where 'food_code_replace' is not 0
merged.loc[merged['food_code_replace'] != 0, 'Food_Code'] = merged['food_code_replace']
merged.loc[merged['food_code_replace'] != 0, 'FDC_Description'] = merged['description_y']

# Drop the unnecessary columns
columns_to_drop = ['New', 'lower_short_description', 'food_code_replace', 'description_y', 'Flag']
merged = merged.drop(columns_to_drop, axis=1)

# Add 'Keyword' column with values before the first comma in 'FDC_Description'
merged['Keyword'] = merged['FDC_Description'].str.split(',', expand=True)[0]

merged.to_csv('../database_cleaned.csv', index=False)

