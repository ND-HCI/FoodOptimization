import pandas as pd
import numpy as np
import json
from sklearn.preprocessing import StandardScaler

def ensure_category_constraints(dataframe, column_name, output_file):
    unique_values = dataframe[column_name].unique().tolist()
    data = {column_name: unique_values}
    
    with open(output_file, 'w') as file:
        json.dump(data, file, indent=4)
        
    print(f"Unique values of '{column_name}' have been saved to '{output_file}'")

def dataset_converter(df, column, id): 

        df = df.dropna(subset=[column])  #adding this 
        df_pivot = df.pivot(index=id, columns=column, values=id).fillna(0).astype(int)
        # df_pivot = df.pivot(index='ID', columns='column', values='ID').fillna(0).astype(int)
        df_pivot[df_pivot > 0] = 1
        df_merged = pd.merge(df, df_pivot, on=id)
        return df_merged

def dataframe_cleanup(dat):

    dat = dat.fillna(0)
    dat = dat[dat['Price'] != 0]
    dat = dat.reset_index(drop=True)

    rename_dict = {
        'Protein': 'Protein - g',
        'Carbohydrate, by difference': "Total Carbohydrate",
        'Sodium, Na': 'Sodium/Salt',
        'Sugars, added': 'Added Sugars',
        'Fatty acids, total saturated': 'Saturated Fat'
    }

    dat = dat.rename(rename_dict, axis=1)

    dat['Protein - cal'] = dat['Protein - g'] * 4
    dat['Carb - cal'] = dat['Total Carbohydrate'] * 4
    dat['Total lipid (fat)'] *= 9
    # dat['Fatty acids, total saturated'] *= 9
    dat['Saturated Fat'] *= 4
    dat['Added Sugars'] *= 4
    # dat['Price per Serving'] = round(dat['Price'] / dat['No Servings'], 2)

    return dat

def convert_to_description(value):
    if value == '0':
        return "Not Important"
    elif value == '1':
        return "Somewhat Important"
    elif value == '2':
        return "Important"

def compute_weights(categories):
    weights = []
    for category in categories:
        if category == "Not Important":
            weights.append(0)
        elif category == "Somewhat Important":
            weights.append(1)
        elif category == "Important":
            weights.append(2)

    # Normalizing weights to sum up to 1
    total = sum(weights)
    if total > 0:
        weights = [weight/total for weight in weights]
    else:  # all are 'Not Important'
        weights = [0.25 for _ in weights]  # all weights are equal

    return weights

def remove_leading_zeroes(cell: str):
    if cell[0] == '0':
        return remove_leading_zeroes(cell[1:])
    return cell

def get_check_digit(upc: str):
    if len(upc) <= 13:
        sm = 0
        for i in range(len(upc)):
            if i % 2 == 0:
                sm += 3*int(upc[i])
            else:
                sm += int(upc[i])
        check_digit = 10 - (sm % 10)
        if check_digit == 10:
            check_digit = 0
        upc += str(check_digit)
        return upc
    elif len(upc) == 14:
        return upc
    else:
        raise ValueError('upc is not right length: {upc}')
    
def id_to_url(id_num):
    # convert id_num to string, remove the last character, and left pad with zeros to length 13
    id_str = str(id_num)[:-1].zfill(13)
    return f"https://www.kroger.com/product/images/medium/front/{id_str}"

def filter_records_by_keywords(filtered_records, match_to_filter_df):
    """
    Filters the records in a DataFrame based on the presence of keywords in the 'Product Name' column.

    Parameters:
    filtered_records (DataFrame): A DataFrame containing a 'Product Name' column.
    match_to_filter_df (list of lists): A list of lists containing keywords.

    Returns:
    DataFrame: The filtered DataFrame.
    """

    # Convert all product names to lowercase for case-insensitive matching
    product_names_lower = filtered_records['Product Name'].str.lower()

    # Flatten the list of lists into a single list of keywords and convert to lowercase
    keywords = [word.lower() for sublist in match_to_filter_df for word in sublist]

    # Check if any keyword is in the Product Name
    contains_keyword = product_names_lower.apply(
        lambda name: any(keyword in name for keyword in keywords))

    # Filter the data if any keyword is present
    return filtered_records[contains_keyword] if contains_keyword.any() else filtered_records

# # Usage example
# filtered_records = filter_records_by_keywords(filtered_records, match_to_filter_df)

def scale_columns(df, columns_to_scale):
    """
    Scales specified columns in a DataFrame using StandardScaler.

    Parameters:
    df (DataFrame): The DataFrame to be scaled.
    columns_to_scale (list): A list of column names in the DataFrame to scale.

    Returns:
    DataFrame: The DataFrame with scaled columns added.
    """

    # Initialize the Standard Scaler
    scaler = StandardScaler()

        # Ensure the data in columns_to_scale is numeric, converting if necessary
    for col in columns_to_scale:
        df[col] = pd.to_numeric(df[col], errors='coerce')  # 'coerce' will set non-convertible values to NaN

    # Handling missing values after conversion (optional, depending on your needs)
    # You can fill NaNs with a specific value or drop them
    df = df.fillna(0)  # For example, fill NaNs with 0
    # or
    # df = df.dropna(subset=columns_to_scale)  # Drop rows where any of the columns_to_scale is NaN

    # Scale the specified columns
    scaled_data = scaler.fit_transform(df[columns_to_scale])

    # Create new column names for the scaled data
    scaled_col_names = [col + '_Scaled' for col in columns_to_scale]

    # Add the scaled data to the DataFrame with new column names
    for i, col_name in enumerate(scaled_col_names):
        df[col_name] = scaled_data[:, i]

    return df

# # Usage example
# optimized_cols = ['Price', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']
# filtered_records = scale_columns(filtered_records, optimized_cols)

def create_unique_keys(user_input_items):
    """
    Creates unique keys for each item in the user input, even if items are duplicated.

    Parameters:
    user_input_items (list): A list of items input by the user.

    Yields:
    str: A unique key for each item in the format "item_index".

    Description:
    This function iterates over the user input items. It keeps track of the number of occurrences 
    of each item and generates a unique key for each occurrence. If an item appears more than once,
    each instance of that item gets a different index appended to it, ensuring uniqueness.
    """

    unique_keys = {}
    for item in user_input_items:
        count = unique_keys.get(item, 0)
        unique_keys[item] = count + 1
        yield f"{item}_{count + 1}"


def process_optimization_output(opt_output, unique_keys, aggregated_results):
    """
    Processes the output of an optimization operation, mapping products to user inputs.

    Parameters:
    opt_output (DataFrame): The output DataFrame from an optimization process.
    unique_keys (iterable): An iterable of unique keys representing user input items.
    aggregated_results (dict): A dictionary to aggregate results where keys are unique 
                               user input items and values are lists of product IDs.

    Description:
    This function iterates over each row of the optimization output. It checks the 'User_Input' 
    column of the output against the unique keys to find a match. When a match is found, the 
    product ID from that row is appended to the corresponding list in the aggregated_results 
    dictionary, thereby mapping products to the specific user inputs they relate to.
    """

    for index, row in opt_output.iterrows():
        category = row['User_Input']
        for key in unique_keys:
            item = key.rsplit('_', 1)[0]  # Get the item name without the occurrence index
            if item.lower() in category.lower():
                product_id = row['UPC Code']  # Assuming 'ID' is the identifier for the product
                aggregated_results[key].append(product_id)


# # example usage
# categories = ["Somewhat Important", "Important", "Somewhat Important", "Somewhat Important"]
# weights = compute_weights(categories)
# print(weights)
