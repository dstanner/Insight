import pandas as pd
import string


# %%

totalwine = pd.read_csv('./img_scraping/item_info/totalwine_info.csv')
liquormart = pd.read_csv('./img_scraping/item_info/liquormart_info.csv')
winetoship = pd.read_csv('./img_scraping/item_info/winetoship_info.csv')

totalwine['source'] = 'totalwine'
liquormart['source'] = 'liquormart'
winetoship['source'] = 'winetoship'

combined = pd.concat([totalwine, liquormart, winetoship])

unique_counts = (combined['Category'].value_counts())

all_cats = list(combined.Category.unique())

rem_cats = ['Ready to Drink', 'Ready To Drink', 'Unavailable',
            'Pre-Mixed Cocktails', 'Prepared Cocktails', 'Colorado', '1',
            'Kentucky', 'Creams', 'USA', 'Mexico', '2013', 'Canada',
            'Missouri', 'Italy', 'Bonded Whiskey', 'Holland', '2011',
            'Sloe Gins & Gin Specialties', 'Islay', 'California',
            'Scottish Ale', 'Fruity', 'Online Beer', 'Norway', 'Red Wines',
            'Sauvignon Blanc', 'Tennessee', 'Sangiovese', 'Germany',
            'Louisiana', 'Pinot Noir / Chardonnay', 'American Macro Lager',
            'Fruit / Vegetable Beer', '2016', 'Sweden', 'Pinot Grigio',
            'Pisco', 'Dessert & Fortified Wine',
            "Robert Parker's Wine Advocate", 'Ireland', 'Light Lageer',
            'Table Wines', 'Gluten-Free', 'Coolers & Malt Beverages',
            'Stout', '18', '2012', 'Light Lager', 'Grappa', "Bitters"]

keep_cats = list(filter(lambda x: x not in rem_cats, all_cats))

combined = combined.loc[combined['Category'].isin(keep_cats)]

# Now get rid of duplicated names and reindex
combined.drop_duplicates(subset="Name", inplace=True)
combined.reset_index(drop=True, inplace=True)

# %% Recode old categories to new categories
combined["Cat"] = combined["Category"]


replace_dict = {
    'Vodka': ["Vodka", "Vodkas - Domestic", 'Vodkas - Imported'],
    'Rum': ['Rum', 'Rums', 'Rums - Flavored'],
    'Scotch': ['Scotch', 'Single Malt Scotch', 'Scotch Whisky',
               'Blended Whiskey'],
    'Tequila': ['Tequila'],
    'Whiskey': ['American Whiskey', 'Canadian Whisky', 'Whisky',
                'Irish Whiskey', 'Whiskey', 'Other Imported Whiskey',
                'Straight Whiskey', 'Tennessee Whiskey',
                'Japanese Whisky', 'Small Batch & Single Barrel Bourbon',
                'Corn Whiskey', 'Bourbon'],
    'Gin': ['Gin', 'Gins & Genevers - Imported', 'Gins - Domestic'],
    'Moonshine': ['White Whiskey/Moonshine'],
    'Flavored Vodka': ['Vodka - Flavored'],
    'Liqueur': ['Liqueur', 'Cordials & Liqueurs - Domestic',
                'Cordials & Liqueurs - Imported', 'Liqueurs/Cordials/Schnapps',
                'Cordials', 'Liquer'],
    'Brandy': ['Brandy', 'Fruit Brandies', 'Brandies - Imported',
               'Calvados', 'Brandy & Cognac', 'Brandies - Domestic',
               'Cognac', 'Cognacs', 'Armagnac'],
    'Soju': ['Soju', 'Shochu'],
    'Schnapps': ['Schnapps'],
    'Flavored Whiskey': ['Flavored Whiskies'],
    'Aperitifs': ['Aperitifs'],
    'Cachaca': ['Cachaca'],
    'Absinthe': ['Absinthe']
}

# Recode old original categories into broad cat labels
new_replace = {v: key for key, vals in replace_dict.items() for v in vals}
combined['Cat'] = combined['Category'].replace(new_replace)
combined

# %% Pull out some other useful categories for liquers from item names

other_cats = {'Triple_sec_Cointreau_Orange_liqueur':['triplesec',
                                                       'cointreau',
                                                       'grangala',
                                                       'grandmarnier'],
              'Anise_Liqueur': ['anisette', 'arak', 'galliano',
                                'herbsaint', 'ouzo', 'pastis',
                                'pernod', 'ricard', 'sambuca'],
              'Amaretto': ['amaretto'],
              'Baileys': ['baileys'],
              'Campari': ['campari'],
              'Frangelico': ['frangelico'],
              'Coffee_Liqueur': ['kahlua', 'coffee', 'caferica',
                                 'tiamaria', 'starbucks'],
              'Flower_liqueur': ['stgermain', 'cremedeviolette',
                                 'cremeyvette', 'rosolio'],
              'Cherry_liqueur': ['cherryheering', 'guignolet', 'maraschino'],
              'Benedictine': ['benedictine'],
              "Aperol": ['aperol'],
              'Chambord': ['chambord'],
              'Chartreuse': ['chartreuse'],
              'Creme_de_Casis': ['cremedecasis'],
              'Creme_de_Coconut': ['cremedecoconut'],
              'Creme_de_Framboise': ['cremedeframboise'],
              'Creme_de_Menthe': ['cremedementhe'],
              'Creme_de_Cacao': ['cremedecacao'],
              'Cynar': ['cynar'],
              'Fernet': ['fernet'],
              'Jaegermeiseter': ['jaegermeister'],
              'Midori': ['midori'],
              'Peppermint Schnapps': ['peppermintschnapps'],
              "Pimm's": ['pimms'],
              'Southern Comfort': ['southerncomfort'],
              'Tuaca': ['tuaca'],
              'Curaco': ['curaco']}

# Turn the values into keys
new_other = {v: key for key, vals in other_cats.items() for v in vals}

# Get names with punctuation and spaces removed, and lowercase
nms = combined.Name.astype('str').tolist()

# Clear punctuation
punc = string.punctuation  # Get punctuation
punc_replace_dict = {punct: None for punct in punc}
punc_replace_trans = nms[0].maketrans(punc_replace_dict)
nms = [x.translate(punc_replace_trans) for x in nms]
nms = [x.replace(" ", "").lower() for x in nms]

# Get indicies to replace
replace_inds = []
name_match = []
new_cat = []
for ind, item in enumerate(nms):
    for name, cat in new_other.items():
        if name in item:
            replace_inds.append(ind)
            name_match.append(name)
            new_cat.append(cat)

# Replace those entries in combined with new category labels
combined.Cat.iloc[replace_inds] = new_cat

# %% Save the file

combined.to_csv('./img_scraping/item_info/all_item_info_categorized.csv',
                index=False)
