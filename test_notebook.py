import cleanup_functions
import json
import pandas as pd

df = pd.read_csv('fdc_kroger_combined_per_serving.csv')
cleanup_functions.ensure_category_constraints(df, "branded_food_category", 'category_cleanup.json')