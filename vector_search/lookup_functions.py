'''
Functions to assist in lookup with recipes from the recipe db,
given input (from a picture).
'''
import json
import random
import pandas as pd
from vector_search import model_mapping
import re

with open('./cocktail/recipe_db_cleaned.json', 'r') as f:
    recipe_db = json.load(f)

with open('./cocktail/liquor_lookup_dict.json', 'r') as f:
    liquor_lookup_db = json.load(f)

with open('./cocktail/rev_liquor_lookup_dict.json', 'r') as f:
    rev_liquor_dict = json.load(f)

with open('./cocktail/recipe_liquor_db.json', 'r') as f:
    recipe_liquor_db = json.load(f)

with open('./object_detection/feature_extraction/master_dict.json', 'r') as f:
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
                print(foo)
                out.append(foo)
                out_text = [x.replace('_',' ') for x in out]
            except Exception as e:
                print(e)
        if len(out) == 0:
            return print("I couldn't quite figure out what the bottle is. "
                    "Make sure each bottle and its label is "
                    "clearly visible.")
        else:
            return list(set(out))

def get_choices(input_set):
    '''
    Scans the recipe_liquor_db, given the set of inputs returned
    from the image search, and returns a list of recipe candidates.

    :param input_set: set of input ingredients
    :return list of recipe IDs matching input
    '''
    choices = []
    for recipe in recipe_liquor_db:
        liquors = {v for k, v in recipe.items() if 'alcohol' in k}
        # Check for the empty set
        if len(liquors) == 0:
            return ("I didn't detect any liquor in your picture. "
                    "Make sure your bottlees are clearly visible, "
                    "and that the labels are facing the camera.")
        else:
            # Turn these into category labels
            cats = {rev_liquor_dict[x] for x in liquors}
            # Get recipe ids that match
            if cats.issubset(input_set):
                choices.append(recipe["idDrink"])
            # Randomize the order
            random.shuffle(choices)
            print(choices)
            return choices


def get_recipe(choices):
    '''
    Gets the first entry from a list of recipe choices.

    :return three full recipes
    '''
    if len(choices) == 0:
        return print("I don't have any more recipes for the bottles I found."
                " Try a new picture, or try uploading"
                " the same picture again.")
    elif len(choices) >= 1:
        r1 = choices.pop(0)
    for recipe in recipe_db:
        if recipe["idDrink"] == r1:
            r1 = recipe
    print(recipe)
    return r1


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
    new_df = pd.DataFrame({'Measures': meas, 'Ingredients': ingrdts})
    out = new_df.to_html(index = False, border = 0, justify = 'left',
                         na_rep="", classes="table", table_id="recipe")

    return name, instructions, out
