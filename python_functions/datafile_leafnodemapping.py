import pandas as pd
from fuzzywuzzy import process, fuzz
from fuzzy_node_mapping import get_highest_scoring_match
from build_tree import create_food_tree
from anytree import PreOrderIter
from tqdm import tqdm

root = create_food_tree('../tree_mapping.csv')  
leaf_nodes = [node.name for node in PreOrderIter(root) if not node.children]

# Load your data
df = pd.read_csv('../walmart_products_10-23-23_3.csv')

print("Starting Mapping...")

# Define a modified get_highest_scoring_match function that uses token_set_ratio
def get_highest_scoring_match_with_token_set_ratio(description, choices):
    return get_highest_scoring_match(description, choices, scorer=fuzz.token_set_ratio)

def apply_with_progress(series, func, *args):
    return series.progress_apply(func, args=args)

tqdm.pandas()
df['Mapping'] = apply_with_progress(df['Product Name'], get_highest_scoring_match, leaf_nodes)

print("Mapping Completed!")

# Save the updated DataFrame to CSV
df.to_csv('../updated_walmart_file.csv', index=False)