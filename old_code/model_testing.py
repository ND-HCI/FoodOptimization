from NutOptimizer import NutOptimizer
import pandas as pd
import numpy as np
import json
from pathlib import Path
from matplotlib import pyplot as plt
import time
from typing import List

#Conversion files needed: 
conversion_factors = pd.read_csv('../data/FoodData_Central_csv_2022-04-28/food_calorie_conversion_factor.csv')
food_conversions = pd.read_csv('../data/FoodData_Central_csv_2022-04-28/food_nutrient_conversion_factor.csv')
conversions = conversion_factors.merge(food_conversions, left_on='food_nutrient_conversion_factor_id', right_on='id')

#Constraint Path called fp
fp = Path('../Data Collection/guidelines/fdc_const.json')

#Main data path called dat_fp
dat_fp = Path('../brand new data/new_fdc_kroger_combined_per_serving.csv')
dat = pd.read_csv(dat_fp)

#Beginning cleanup of main datafile
dat = dat.fillna(0)

#Renaiming two of the headers: 
rename_dict = {
               'Protein': 'Protein - g',
               'Carbohydrate, by difference': "Total Carbohydrate"
              }

dat = dat.rename(rename_dict, axis=1)

# Conversions: sugar from g to kcal, total lipid g to kcal, Fatty acids total saturated g to kcal, Vitamin A iu to mcg RAE
dat['Protein - cal'] = dat['Protein - g'] * 4 
dat['Carb - cal'] = dat['Total Carbohydrate'] * 4
dat['Total lipid (fat)'] *= 9
dat['Fatty acids, total saturated'] *= 9
dat['Sugars, total including NLEA'] *= 4
dat['Sugars, added'] *= 4
dat['Price per Serving'] = round(dat['Price'] / dat['No Servings'], 2)

# Category/List Items
cats = pd.read_csv('../data/categories.csv')

#filters cat dataframe where category is only present in column 'branded_food_category' 
cats = cats[cats['Category'].isin(dat['branded_food_category'])]

#new category values
def new_cat(row: pd.DataFrame):
    if pd.isna(row['Level 3 Categorization']):
        return row['Category']
    return row['Level 3 Categorization']

#New column Final Category that has the list of categories
cats['Final Category'] = cats.apply(new_cat, axis=1)
# #
cats_dict = {}
for idx, row in cats.iterrows():
    cats_dict[row['Category']] = row['Final Category']

# Add indicator columns for categories
categories = dat['branded_food_category'].unique()

for cat in categories:
    dat.loc[dat['branded_food_category'] == cat, cats_dict[cat]] = 1
    dat.loc[dat['branded_food_category'] == cat, 'final_category'] = cats_dict[cat]
    
dat = dat.fillna(0)
dat = dat[dat['Price'] != 0]
dat = dat.reset_index(drop=True)

pd.set_option('display.max_columns', 250)

dat.to_csv('second_one.csv', index=False)
    
# Add weights for optimization constraints
category_weights = ['Protein Foods', 'Grains']
for cat in category_weights:
    dat.loc[dat['final_category'] == cat, cat+'_wt_in_g'] = dat.loc[dat['final_category'] == cat, 'serving_size']
    
dat = dat.fillna(0)

# Drop Categories which we don't want
level_2_cats = cats[cats['Level 2'] == 'Include']['Category']

level_2_dat = dat[dat['branded_food_category'].isin(level_2_cats)]
level_2_dat = level_2_dat.reset_index(drop=True)

dat.to_csv('third_one.csv', index=False)

opt = NutOptimizer(data=dat)
opt.load_constraints_json(fp)

level_2_opt = NutOptimizer(data=level_2_dat)
level_2_opt.load_constraints_json(fp)

constraints = opt.get_models()
level_2_constraints = level_2_opt.get_models()

for name in constraints:
    if name not in ['F 31-50', 'M 31-50']:
        opt.remove_model(name)
        level_2_opt.remove_model(name)

# No category restrictions
opt.optimize_all('Price per Serving', verbose=False, var_type='INTEGER')
int_res = opt.get_all_results()
int_cost = opt.get_all_optimal_values('Price per Serving')

print("Original Data - F 31-50 - Integer Optimization")
original_integer_fem_res = round(opt.get_one_optimal_value("F 31-50", "Price per Serving"),2)
original_integer_male_res = round(opt.get_one_optimal_value("M 31-50", "Price per Serving"),2)
pd.DataFrame(int_res['F 31-50'])[['ID', 'Description', 'branded_food_category', 'Price per Serving', 'Amount']]
