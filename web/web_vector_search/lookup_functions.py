'''
Functions to assist in lookup with recipes from the recipe db,
given input (from a picture).
'''
import json
import random
import pandas as pd
from web_vector_search import model_mapping
import re

with open('./model_files/recipe_db_cleaned.json', 'r') as f:
    recipe_db = json.load(f)

with open('./model_files/liquor_lookup_dict.json', 'r') as f:
    liquor_lookup_db = json.load(f)

with open('./model_files/rev_liquor_lookup_dict.json', 'r') as f:
    rev_liquor_dict = json.load(f)

with open('./model_files/recipe_liquor_db.json', 'r') as f:
    recipe_liquor_db = json.load(f)

with open('./model_files/master_dict.json', 'r') as f:
    master_dict = json.load(f)


def return_output(inds):
    '''
    Takes a list of indices returned by vector_search.retrieve_img_data
        and returns a set of detected liquor categories.

    This output strings will need to be formatted prior to printing
    in order to remove the _ between spaces.
    '''
    out = []
    if len(inds) == 0:
        print("I couldn't quite figure out what the bottle is. "
              "Try a clearer picture.")
    else:
        for bottle in inds:
            try:
                foo = master_dict[str(bottle)]['Cat']
                out.append(foo)
                out_text = [x.replace('_',' ') for x in out]
            except Exception as e:
                print(e)
        if len(out) == 0:
            print("I couldn't quite figure out what the bottle is. "
                  "Make sure each bottle and its label is "
                  "clearly visible.")
        else:
            return set(out)

def get_choices(input_set):
    '''
    Scans the recipe_liquor_db, given the set of inputs returned
    from the image search, and returns a list of recipe candidates.

    :param input_set: set of input ingredients
    :return list of recipe IDs matching input
    '''
    input_set = set(input_set)
    choices = []
    for recipe in recipe_liquor_db:
        liquors = []
        for k, v in recipe.items():
            if 'alcohol' in k:
                liquors.append(v)
        liquors = set(liquors)
        # Turn these into category labels
        cats = {rev_liquor_dict[x] for x in liquors}
        # Get recipe ids that match
        if len(cats) == 0:
            continue
        elif cats.issubset(input_set):
            choices.append(recipe["idDrink"])
    # Randomize the order
    random.shuffle(choices)

    return choices


def get_recipe(choices, idx):
    '''
    Gets the first entry from a list of recipe choices.

    :return full recipes
    '''
    r = choices[idx]
    for recipe in recipe_db:
        if recipe["idDrink"] == r:
            rec = recipe
    return rec


def format_recipe(recipe):
    '''
    Gets information from the recipe retruned by get_recipe.

    Returns 3 items:
        Name of cocktail
        Instructions for making cocktail
        html-formatted table for ingredients
    '''
    for k, v in recipe.items():
        recipe[k] = [v]
    df = pd.DataFrame(recipe)
    name = df['strDrink'].loc[0]
    instructions = df['strInstructions'].loc[0]
    drop_cols = []
    for x in df.columns:
        if not 'Ingred' in x:
            if not 'Meas' in x:
                drop_cols.append(x)
    df.drop(drop_cols, inplace=True, axis = 1)
    meas_cols = [x for x in df.columns if "Meas" in x]
    ingrdts_cols = [x for x in df.columns if "Ingred" in x]
    meas_df = df[meas_cols]
    ingrdts_df = df[ingrdts_cols]

    meas_melt = meas_df.T
    meas_melt = meas_melt[0]
    meas = meas_melt.tolist()
    ingrdts_melt = ingrdts_df.T
    ingrdts_melt = ingrdts_melt[0]
    ingrdts = ingrdts_melt.tolist()

    new_df = pd.DataFrame({'Measures': pd.Series(meas),
                           'Ingredients': pd.Series(ingrdts)})
    out = new_df.to_html(index = False, border = 0, justify = 'left',
                         na_rep="", classes="table", table_id="recipe")

    return name, instructions, out
