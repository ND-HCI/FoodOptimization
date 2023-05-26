import pandas as pd
import numpy as np

# Set pandas display options
pd.set_option('display.max_columns', None)

def remove_leading_zeroes(cell: str):
    if cell[0] == '0':
        return remove_leading_zeroes(cell[1:])
    return cell

def get_check_digit(upc: str):
    if len(upc) <= 13:
        sm = 0
        for i in range(len(upc)):
            if i % 2 == 0:
                sm += 3*int(upc[i])
            else:
                sm += int(upc[i])
        check_digit = 10 - (sm % 10)
        if check_digit == 10:
            check_digit = 0
        upc += str(check_digit)
        return upc
    elif len(upc) == 14:
        return upc
    else:
        raise ValueError('upc is not right length: {upc}')


wic = pd.read_excel('WIC.xlsx', dtype={'UPC_Code': str})

wic = wic[['CATEGORY CODE', 'CATEGORY DESCRIPTION', 'SUBCATEGORY CODE',
       'SUBCATEGORY DESCRIPTION', 'UPC CODE', 'BRAND NAME', 'FOOD DESCRIPTION',
       'PACKAGE SIZE', 'UNIT OF MEASURE']]

wic = wic.rename(columns={'CATEGORY CODE': 'CATEGORY_CODE', 'CATEGORY DESCRIPTION': 'CATEGORY_DESCRIPTION', 
                        'SUBCATEGORY CODE': 'SUBCATEGORY_CODE', 'SUBCATEGORY DESCRIPTION': 'SUBCATEGORY_DESCRIPTION',
                        'UPC CODE': 'UPC_CODE', 'BRAND NAME': 'BRAND_NAME',
                        'FOOD DESCRIPTION': 'FOOD_DESCRIPTION', 'PACKAGE SIZE': 'PACKAGE_SIZE',
                        'UNIT OF MEASURE': 'UNIT_OF_MEASURE'})

# wic['UPC_CODE'] = wic['UPC_CODE'].astype(str).apply(get_check_digit)
wic['UPC_CODE'] = wic['UPC_CODE'].astype(str).apply(remove_leading_zeroes)



# kroger = pd.read_csv('fdc_kroger_combined_per_serving.csv', dtype={'ID': str, 'gtin_upc': str})

# duplicate_wic_upc = wic[wic['UPC_CODE'].duplicated()]
# print(f"Number of duplicate UPC_CODE in WIC: {len(duplicate_wic_upc)}")

# # 2. Find duplicate ID in Kroger
# duplicate_kroger_id = kroger[kroger['gtin_upc'].duplicated()]
# print(f"Number of duplicate ID in Kroger: {len(duplicate_kroger_id)}")

# # 3. Find matches between UPC_CODE in WIC and ID in Kroger
# matches = kroger['gtin_upc'].isin(wic['UPC_CODE'])
# print(f"Number of matches between UPC_CODE in WIC and ID in Kroger: {matches.sum()}")


