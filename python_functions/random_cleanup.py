import pandas as pd

# Assuming df is your dataframe
df = pd.read_csv('mergedFNDDS.csv')  # Replace 'your_file.csv' with your actual csv file path

df['lower_short_description'] = df['short_description'].str.lower()

# Drop the duplicate rows based on 'lower_short_description', keeping only the first occurrence
unique_df = df.drop_duplicates(subset='lower_short_description', keep='first')

# Create a dictionary where keys are 'lower_short_description' and values are 'food_code'
unique_dict = dict(zip(unique_df['lower_short_description'], unique_df['food_code']))

# Convert dictionary to DataFrame
unique_df = pd.DataFrame.from_dict(unique_dict, orient='index', columns=['food_code'])

# Write DataFrame to csv file
unique_df.to_csv('unique_values.csv', index_label='lower_short_description')
