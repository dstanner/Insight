"""
Augment labeled images from liquor category folders.
Save Augmented images, to Augmented folder,
Then re-organize back into category folders.
"""
from keras.preprocessing.image import ImageDataGenerator
import os
import shutil
import random
import math
from collections import Counter
from itertools import repeat
import json
import pandas as pd


# %% Make augmenter objects

path = './object_detection/cat_organized_ref_img/'

datagen = ImageDataGenerator(
        rotation_range=40,
        width_shift_range=0.25,
        height_shift_range=0.25,
        shear_range=0.4,
        zoom_range=0.3,
        horizontal_flip=False,
        rescale = 1./255,
        fill_mode='nearest')

augmenter = datagen.flow_from_directory(
    path,
    target_size = (224, 224),
    batch_size = 1,
    shuffle = False,
    seed = 101,
    save_to_dir = './object_detection/augmented/')

# %% Create and save augmented images
# Generate 3 augmented images per image
n_break = augmenter.n *3

i = 0
for batch in augmenter:
    print(i,"/",n_break)
    i += 1
    if i == n_break:
        break

# %% Get dictionary for mapping between augmented file names and original items

input_files = augmenter.filenames

with open('./object_detection/augmenter_original_file_list.txt', 'w') as f:
    f.write('\n'.join(input_files))

with open('./object_detection/augmenter_original_file_list.txt', 'r') as f:
    input_files = f.readlines()
input_files = [x.replace('\n', '') for x in input_files]

path = './object_detection/augmented/'
generated_files = os.listdir(path)
generated_files = [x for x in generated_files if '.DS' not in x]


# The generated list is ordered as 0, 1, 1000 (e.g., alphabetial
# order), not numbered order.  Fix this.
generated_files.sort(key = lambda x: int(x.split('_')[1]))
generated_files[:250]  # fixed

foo = [x.split('_')[1] for x in generated_files]
counts = Counter(foo)
non_3_items = {k: v for k, v in counts.items() if v != 3}
non_3_items # None.


with open('./object_detection/augmented_file_list.txt', 'w') as f:
    f.write('\n'.join(generated_files))
with open('./object_detection/augmented_file_list.txt', 'r') as f:
    generated_files = f.readlines()
generated_files = [x.replace('\n', '') for x in generated_files]
generated_files = [x for x in generated_files if '.DS' not in x]

# Get a mapping dictionary linking augmented file names
# to their input file counterparts

rep_input = [x.split('/')[-1] for x in input_files for _ in (0, 1, 2)]

rep_input
generated_files
mapping_dict = dict(zip(generated_files, rep_input))

with open('./object_detection/augmented_file_mapping.json', 'w') as f:
    json.dump(mapping_dict, f)
