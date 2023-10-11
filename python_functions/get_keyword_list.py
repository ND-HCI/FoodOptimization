import pandas as pd

def lookup_food_codes(food_codes_list, data_file):
    # Read the data file into a pandas DataFrame
    df = pd.read_csv(data_file, dtype={'food_code': str})  # Make sure 'food_code' column is read as string

    # Check if 'food_code' and 'short_description' columns exist in the DataFrame
    if 'food_code' not in df.columns or 'short_description' not in df.columns:
        raise ValueError("'food_code' or 'short_description' does not exist in the DataFrame.")

    # Filter the DataFrame to get only the rows where food_code is in the food_codes_list
    filtered_df = df[df['food_code'].isin(food_codes_list)]

    # Set the DataFrame's index to the food_code column
    filtered_df.set_index('food_code', inplace=True)

    # Re-index the DataFrame using the original food_codes_list, this will ensure the order is preserved
    filtered_df = filtered_df.reindex(food_codes_list)

    # Get the list of 'short_description' corresponding to the food codes
    descriptions_list = filtered_df['short_description'].tolist()

    return descriptions_list

def check_element_type(element_list):
    types_set = {type(element) for element in element_list}
    return types_set

def test_lookup_food_codes():
    food_codes_list = ['1001', '1003']
    data_file = 'sample_data.csv'
    descriptions = lookup_food_codes(food_codes_list, data_file)
    print(f"Descriptions for food codes {food_codes_list}: {descriptions}")

if __name__ == '__main__':
    print("Testing lookup_food_codes:")
    test_lookup_food_codes()


# #Testing
# food_codes_list = ['14202010']  # Replace with your list of food codes
# data_file = 'mergedFNDDS.csv'
# descriptions = lookup_food_codes(food_codes_list, data_file)
# print(descriptions)

# # Check the types of the returned descriptions
# types_set = check_element_type(descriptions)
# print(types_set)
