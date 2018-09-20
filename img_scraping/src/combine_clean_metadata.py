import pandas as pd
import os

# %%
os.chdir('/Users/Darren/Documents/GitHub/Insight/img_scraping/src')

totalwine = pd.read_csv('../item_info/totalwine_info.csv')
liquormart = pd.read_csv('../item_info/liquormart_info.csv')
winetoship = pd.read_csv('../item_info/winetoship_info.csv')

totalwine['source'] = 'totalwine'
liquormart['source'] = 'liquormart'
winetoship['source'] = 'winetoship'

combined = pd.concat([totalwine, liquormart, winetoship])

unique_counts = (combined['Category'].value_counts())

all_cats = list(combined.Category.unique())

rem_cats = ['Ready to Drink', 'Ready To Drink', 'Unavailable',
            'Pre-Mixed Cocktails', 'Prepared Cocktails', 'Colorado', '1',
            'Kentucky', 'Creams', 'USA', 'Mexico', 'Bitters', '2013', 'Canada',
            'Missouri', 'Italy', 'Bonded Whiskey', 'Holland', '2011',
            'Sloe Gins & Gin Specialties', 'Islay', 'California',
            'Scottish Ale', 'Fruity', 'Online Beer', 'Norway', 'Red Wines',
            'Sauvignon Blanc', 'Tennessee', 'Sangiovese', 'Germany',
            'Louisiana', 'Pinot Noir / Chardonnay', 'American Macro Lager',
            'Fruit / Vegetable Beer', '2016', 'Sweden', 'Pinot Grigio',
            'Pisco', 'Dessert & Fortified Wine',
            "Robert Parker's Wine Advocate", 'Ireland', 'Light Lageer',
            'Table Wines', 'Gluten-Free', 'Coolers & Malt Beverages',
            'Stout', '18', '2012', 'Light Lager']

keep_cats = list(filter(lambda x: x not in rem_cats, all_cats))

combined = combined.loc[combined['Category'].isin(keep_cats)]

# %% Recode old categories to new categories
combined["Cat"] = combined["Category"]


replace_dict = {
    'Vodka': ["Vodka", "Vodkas - Domestic", 'Vodkas - Imported'],
    'Rum': ['Rum', 'Rums', 'Rums - Flavored'],
    'Scotch': ['Scotch', 'Single Malt Scotch', 'Scotch Whisky',
               'Blended Whiskey'],
    'Tequila': ['Tequila'],
    'Bourbon': ['Bourbon'],
    'Whiskey': ['American Whiskey', 'Canadian Whisky', 'Whisky',
                'Irish Whiskey', 'Whiskey', 'Other Imported Whiskey',
                'Straight Whiskey', 'Tennessee Whiskey',
                'Japanese Whisky', 'Small Batch & Single Barrel Bourbon',
                'Corn Whiskey'],
    'Gin': ['Gin', 'Gins & Genevers - Imported', 'Gins - Domestic'],
    'Moonshine': ['White Whiskey/Moonshine'],
    'Flavored Vodka': ['Vodka - Flavored'],
    'Liqueur': ['Liqueur', 'Cordials & Liqueurs - Domestic',
                'Cordials & Liqueurs - Imported', 'Liqueurs/Cordials/Schnapps',
                'Cordials'],
    'Cognac': ['Cognac', 'Cognacs', 'Armagnac'],
    'Brandy': ['Brandy', 'Fruit Brandies', 'Brandies - Imported',
               'Calvados', 'Brandy & Cognac'],
    'Soju': ['Soju', 'Shochu'],
    'Schnapps': ['Schnapps'],
    'Grappa': ['Grappa'],
    'Flavored Whiskey': ['Flavored Whiskies'],
    'Aperitifs': ['Aperitifs'],
    'Cachaca': ['Cachaca'],
    'Absinthe': ['Absinthe']
}

# %% Recode old original categories into broad cat labels

new_replace = {v: key for key, vals in replace_dict.items() for v in vals}
combined['Cat'] = combined['Category'].replace(new_replace)
combined.to_csv('../item_info/all_item_info_categorized.csv', index=False)
