import pandas as pd
import os
import re
from shutil import copyfile
import json
import string

# Load metadata
info = pd.read_csv('./img_scraping/item_info/all_item_info_categorized.csv')

# Get list of cropped images
cropped_files = os.listdir('./object_detection/ref_img_cropping/cropped_images/')
cropped_files = [x for x in cropped_files if '.DS' not in x]
cropped_files

# Rename files, to remove all punctuation and make lowercase.
# First, strip off the .png extension.
cropped_names = [re.sub('.png', '', x) for x in cropped_files]
cropped_names = [x for x in cropped_names if '.DS' not in x]
translator = str.maketrans('', '', string.punctuation)
cropped_names = [x.translate(translator).lower() for x in cropped_names]

cropped_names


# Get source_name from metadata df
sources = info.source.tolist()
names = info.Name.tolist()
names = [x.replace(" ", "_") for x in names]
names


source_names = []
for i in range(len(names)):
    source_names.append(sources[i] + names[i])
source_names = [x.translate(translator).lower() for x in source_names]
source_names

# Get categories from df
cats = info.Cat.tolist()
info.Cat.nunique()
# Get categories for each name
pic_categories = {}
for name in cropped_names:
    for ind, string in enumerate(source_names):
        if string in name:
            pic_categories[name] = cats[ind]

len(set(pic_categories.keys()))

pic_categories
included_categories = list(set(pic_categories.values()))

# Make directories for each category
path = './object_detection/cat_organized_ref_img/'

for cat in included_categories:
    if not os.path.exists(path + cat):
        os.makedirs(path + cat)

# Prepare to copy the files
source_dir = './object_detection/ref_img_cropping/cropped_images/'
dest_dir = './object_detection/cat_organized_ref_img/'

# copy files to category directories, and save a dictionary
for name, cat in pic_categories.items():
    for idx, file in enumerate(cropped_names):
        if file in name:
            source_path = os.path.join(source_dir, cropped_files[idx])
            new_path = os.path.join(dest_dir, cat, name + '.png')
            copyfile(source_path, new_path)


with open('./object_detection/pic_lookup_dictionary.json', 'w') as f:
    json.dump(pic_categories, f)
