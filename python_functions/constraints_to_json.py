import pandas as pd
import json

def unique_values_to_json(csv_file, column_name, json_file):
    # Read the CSV data
    df = pd.read_csv(csv_file)

    # Check if the column exists in the DataFrame
    if column_name not in df.columns:
        raise ValueError(f"'{column_name}' does not exist in the DataFrame.")

    # Get the unique values from the column
    unique_values = df[column_name].unique().tolist()

    # Add the unique values to a dictionary under the given keyword
    data = {column_name: unique_values}

    # Write these values into a JSON file
    with open(json_file, 'w') as f:
        json.dump(data, f)

    print(f"Unique values from '{column_name}' have been written to '{json_file}'.")

# Usage:
unique_values_to_json('../database_fullgrocery_testfile.csv', 'Keyword', '../foodcode_output.json')
