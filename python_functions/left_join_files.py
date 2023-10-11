import pandas as pd

import pandas as pd

# NOTE: THIS WILL NEED TO BE REDONE BASED ON THE OTHER DATAFRAME WITH THE FOODCODES 
import pandas as pd

def join_csv_files(file1, file2, join_columns):
    # Load the data from the CSV files
    df1 = pd.read_csv(file1, dtype={"Food_Code": str})
    df2 = pd.read_csv(file2, dtype={"Food_Code": str})

    # Perform a left join on the specified columns
    merged = pd.merge(df1, df2, on=join_columns, how='left')

    # Remove duplicate rows
    merged = merged.drop_duplicates(subset=join_columns)

    # Remove rows where 'Food_Code' is 0 or "0"
    merged = merged[merged['Food_Code'] != "0"]

    # Count the number of non-null values in the joined columns
    num_matches = merged[join_columns].dropna().shape[0]

    print(f"Number of rows in the first file: {len(df1)}")
    print(f"Number of matching rows after join: {num_matches}")

    return merged


# Usage:
join_columns = ['Description', 'ingredients']
merged_df = join_csv_files('../fdc_kroger_combined_per_serving.csv', 'kroger_foodcode_output.csv', join_columns)
merged_df.to_csv('../database_fullgrocery_testfile.csv', index=False)
