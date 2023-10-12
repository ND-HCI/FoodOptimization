import pandas as pd
from food_tree import create_food_tree

import pandas as pd

def add_parent_and_grandparent_columns(tree_root, name_to_node, input_csv_file, output_csv_file):
    df = pd.read_csv(input_csv_file)

    # Add new columns
    df['Parent'] = ''
    df['Grandparent'] = ''

    # Debug: Print out node names and the first few rows of your DataFrame
    print("Node names:", list(name_to_node.keys()))
    print("First few rows of DataFrame:", df.head())

    for idx, row in df.iterrows():
        keyword = row['Keyword']

        if keyword in name_to_node:
            node = name_to_node[keyword]

            if node.parent is not None:
                df.at[idx, 'Parent'] = node.parent.name
                
                if node.parent.parent is not None:
                    df.at[idx, 'Grandparent'] = node.parent.parent.name
        else:
            print(f"Keyword {keyword} not found in node names.")  # Debug: Print out keywords that are not found

    # Save the DataFrame to a new csv file
    df.to_csv(output_csv_file, index=False)


# Run the function
root, name_to_node = create_food_tree(
    schema_file='../schema.csv',
    food_file='../food.csv',
    survey_file='../survey_fndds_food.csv',
    wweia_file='../wweia_food_category.csv'
)

# add_parent_and_grandparent_columns(root, name_to_node, '../database_fullgrocery_testfile.csv', '../database_fullgrocery_with_parents.csv')

add_parent_and_grandparent_columns(root, name_to_node, '../database_cleaned.csv', '../database_cleaned_fullgrocery_with_parents.csv')

