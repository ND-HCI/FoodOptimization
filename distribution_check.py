import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import seaborn as sns
import cleanup_functions

dat_fp = ('fdc_kroger_combined_per_serving.csv')
dat = pd.read_csv(dat_fp)


df = cleanup_functions.dataframe_cleanup(dat)
print(df)

# List of column names
cols = ['Price per Serving', 'Sodium/Salt', 'Saturated Fat', 'Added Sugars']

# Loop through the columns and plot histograms
for col in cols:
    plt.figure(figsize=(10, 6))
    sns.histplot(df[col], bins=30, kde=True)
    plt.title(f'Distribution of {col}')
    plt.show()
