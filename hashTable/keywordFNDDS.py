import pandas as pd
import json

# Load data from json file
with open('FoodData_Central.json', 'r') as f:
    data = json.load(f)

# Extract "description" field from each item in "Survey Foods"
descriptions = [item['Description'] for item in data['SurveyFoods']]
 
# Split each description by comma and take the first part
descriptions = [desc.split(',')[0] for desc in descriptions]

# Remove duplicates by converting to a set and back to a list
descriptions = list(set(descriptions))

# Create a DataFrame from the list of descriptions
df = pd.DataFrame(descriptions, columns=['description'])

# Save DataFrame to csv file
df.to_csv('output_of_keywords.csv', index=False)
