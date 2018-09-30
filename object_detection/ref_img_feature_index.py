from vector_search import vector_search
import os
import re
from keras.models import load_model
import json
import numpy as np
import collections
import pandas as pd


# %% Get picture files list ready
'''
Gets the list of files to be feature-extracted and indexed
'''
# Get the cropped image files
cropped_img_folder = './object_detection/cat_organized_ref_img/'

orig_images = []
for root, dirs, files in os.walk(cropped_img_folder):
    for name in files:
        orig_images.append(os.path.join(root, name))
orig_images =[x for x in orig_images if '.DS' not in x]


# %% Load a model if needed

# Load model and build with model weights
model = vector_search.load_headless_pretrained_model()

# Save model
model.save('./object_detection/feature_extraction/headlessVGG16.h5')

# %% Extract features for reference database
'''
Extract the features from the object_detection/augmented/training/
images folder and save them and their file mappings.
'''

# Load saved model
model = load_model('./object_detection/feature_extraction/headlessVGG16.h5')

# Extract features and file mappings and save them to disk
features, file_mapping = vector_search.generate_features_file(orig_images,
                                                              model)

# Error in save_features for file_mapping, so brute force save
np.save('./object_detection/feature_extraction/ref_img_features_no_aug.npy', features)
with open('./object_detection/feature_extraction/ref_img_filemapping_no_aug.json', 'w') as f:
    json.dump(file_mapping, f)

# %% Build database reference features
'''
Build and save an ANNOY search index for fast searching.
'''
# Load the saved features and file mappings and compile Annoy search indices
features, file_index = vector_search.load_features(
    'object_detection/feature_extraction/ref_img_features_no_aug',
    './object_detection/feature_extraction/ref_img_filemapping_no_aug')

ref_img_index = vector_search.index_features(features, n_trees=8000)

ref_img_index.save('./object_detection/feature_extraction/ref_img_index_no_aug.ann')

# %%
'''
Get and save hash dictionary mapping between the file_mapping index,
and each the item name, category, source website, local source file path,
and the local source file name.
'''

with open('./object_detection/feature_extraction/ref_img_filemapping_no_aug.json', 'r') as f:
    ref_img_filemapping = json.load(f)

with open('./object_detection/pic_lookup_dictionary.json', 'r') as f:
    name_cat_dict = json.load(f)

master_dict = {}
for idx, file in ref_img_filemapping.items():
    cat = file.split('/')[3]
    name = file.split('/')[4]
    name.replace('.png', '')
    container_dict = {}
    container_dict['Cat'] = cat
    container_dict['Name'] = name
    master_dict[idx] = container_dict

with open('./object_detection/feature_extraction/master_dict.json', 'w') as f:
    json.dump(master_dict, f)
