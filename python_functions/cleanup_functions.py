import pandas as pd
import numpy as np
import json

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


# example usage
categories = ["Somewhat Important", "Important", "Somewhat Important", "Somewhat Important"]
weights = compute_weights(categories)
print(weights)
