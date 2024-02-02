import openai

openai.api_key = "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"

def get_best_categories(user_items, categories_list, model="gpt-3.5-turbo"):
    matched_categories = []
    categories_string = ", ".join(categories_list)  # Prepare the categories as a string
    
    system_message = f'Given the list item, return the most relevant category for the item.'

    for item in user_items:
        try:
            # Prepare the chat messages
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": f"Given the categories: {categories_string}. What is the most relevant category for the item: {item}?  Just return the category_string."}
            ]
            
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                max_tokens=10
            )
            matched_category = response.choices[0].message["content"].strip()
            matched_categories.append(matched_category)
        except Exception as e:
            print(f"Error processing item {item}: {e}")
            matched_categories.append("Error")
            
    return matched_categories

# Example usage:
user_items = ["cheese", "bread", "pasta"]
categories_list = ["Dairy Products", "Bakery Items", "Pasta & Noodles", "Meat & Poultry"]
matched_categories = get_best_categories(user_items, categories_list)
print(matched_categories)
