import pandas as pd
import os
import re
from shutil import copyfile
import json

# Load metadata
info = pd.read_csv('./img_scraping/item_info/all_item_info_categorized.csv')

# Get list of cropped images
cropped_files = os.listdir('./object_detection/ref_img_cropping/cropped_images/')
cropped_files

# Extract source_name from cropped images
cropped_names = [re.sub('crop_[0-9]_','', x) for x in cropped_files]
cropped_names = [re.sub('.png', '', x) for x in cropped_names]
cropped_names = [x for x in cropped_names if '.DS' not in x]
cropped_names


# Get source_name from metadata df
sources = info.source.tolist()
names = info.Name.tolist()
names = [x.replace(" ", "_") for x in names]



source_names = []
for i in range(len(names)):
    source_names.append(sources[i] + '_' + names[i])
source_names

# Get categories from df
cats = info.Cat.tolist()
info.Cat.nunique()
# Get categories for each name
pic_categories = {}
for name in cropped_names:
    for ind, string in enumerate(source_names):
        if name in string:
            pic_categories[name] = cats[ind]

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
pic_lookup_dictionary = {}
for name, cat in pic_categories.items():
    for file in cropped_files:
        if name in file:
            #copyfile(source_dir + file, dest_dir + cat + '/' + file)
            pic_lookup_dictionary[file] = cat

pic_lookup_dictionary

with open('pic_lookup_dictionary.json', 'w') as f:
    json.dump(pic_lookup_dictionary, f)
