import pandas as pd

def split_description(df):
    # Ensure 'FDC_Description' is string type
    df['FDC_Description'] = df['FDC_Description'].astype(str)

    # split the 'FDC_Description' column at the first comma
    df['Keyword'] = df['FDC_Description'].apply(lambda x: x.split(',', 1)[0])
    
    # return the modified dataframe
    return df

# read your CSV file into a DataFrame
df = pd.read_csv("../database_fullgrocery_testfile.csv")

# pass the DataFrame to your function
df = split_description(df)

# write the DataFrame back to a CSV file
df.to_csv('../database_fullgrocery_testfile.csv', index=False)
