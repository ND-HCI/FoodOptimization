import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler

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

    # Scale the specified columns
    scaled_data = scaler.fit_transform(df[columns_to_scale])

    # Create new column names for the scaled data
    scaled_col_names = [col + '_Scaled' for col in columns_to_scale]

    # Add the scaled data to the DataFrame with new column names
    for i, col_name in enumerate(scaled_col_names):
        df[col_name] = scaled_data[:, i]

    return df

