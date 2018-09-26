"""
Augment labeled images from liquor category folders.
Save Augmented images, to Augmented folder,
Then re-organize back into category folders.

Split augmented data into training and validation sets.
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
        rotation_range=20,
        width_shift_range=0.1,
        height_shift_range=0.1,
        shear_range=0.25,
        zoom_range=0.15,
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

# input_files = augmenter.filenames

# with open('./object_detection/original_file_list.txt', 'w') as f:
#     f.write('\n'.join(input_files))

with open('./object_detection/original_file_list.txt', 'r') as f:
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

# Now create a list of repeated input file names
repeated_input_files = []
for item in input_files:
    repeats = repeat(item, 3)
    repeated_input_files.extend(repeats)

# Check that the counts are correct
counts = Counter(repeated_input_files)
check_counts = {k: v for k, v in counts.items() if v != 3}
check_counts.keys() # All good.


augmented_files_dictionary = dict(zip(generated_files, repeated_input_files))
augmented_files_dictionary

with open('./object_detection/augmented_files_dictionary.json', 'w') as f:
    f.write(json.dumps(augmented_files_dictionary))

with open('./object_detection/augmented_files_dictionary.json', 'r') as f:
    augmented_files_dictionary = json.load(f)

# %% Get rid of some image files from poor crops; I manually inspected these
# and saw that they're not good crops.
delete_numbers = ['_17_', '_51_', '_53_', '_55_', '_64_', '_66_',
                   '_91_', '_106_', '_107_', '_121_', '_124_', '_135_',
                   '_177_', '_193_', '_207_', '_209_', '_210_', '_225_',
                   '_235_', '_239_', '_241_', '_247_', '_280_', '_317_',
                   '_323_', '_388_', '_391_', '_393_', '_401_', '_402_',
                   '_412_', '_456_', '_499_', '_510_', '_511_', '_522_',
                   '_526_', '_545_', '_547_', '_552_', '_578_', '_595_',
                   '_599_', '_601_', '_632_', '_634_', '_635_', '_636_',
                   '_638_', '_646_', '_649_', '_656_', '_674_', '_675_',
                   '_734_', '_736_', '_762_', '_777_', '_778_', '_779_',
                   '_783_', '_809_', '_823_', '_828_', '_829_', '_860_',
                   '_907_', '_914_', '_947_', '_948_', '_955_', '_980_',
                   '_982_', '_996_', '_1001_', '_1018_', '_1043_', '_1044_',
                   '_1052_', '_1063_', '_1068_', '_1069_', '_1093_', '_1095_',
                   '_1104_', '_1105_', '_1107_', '_1117_', '_1133_', '_1143_',
                   '_1183_', '_1184_', '_1189_', '_1190_', '_1204_', '_1205_',
                   '_1211_', '_1217_', '_1221_', '_1249_', '_1250_', '_1263_',
                   '_1267_', '_1273_', '_1278_', '_1314_', '_1320_', '_1322_',
                   '_1328_', '_1332_', '_1346_', '_1351_', '_1371_', '_1392_',
                   '_1396_', '_1414_', '_1432_', '_1446_', '_1462_', '_1483_',
                   '_1484_', '_1488_', '_1490_', '_1491_', '_1492_', '_1497_',
                   '_1501_', '_1595_', '_1601_', '_1616_', '_1624_', '_1627_',
                   '_1628_', '_1631_', '_1632_', '_1636_', '_1637_', '_1638_',
                   '_1640_', '_1641_', '_1669_', '_1674_', '_1681_', '_1683_',
                   '_1692_', '_1699_', '_1705_', '_1729_', '_1737_', '_1738_',
                   '_1742_', '_1752_', '_1774_', '_1789_', '_1800_', '_1813_',
                   '_1814_', '_1815_', '_1816_', '_1820_', '_1826_', '_1843_',
                   '_1845_', '_1886_', '_1887_', '_1893_', '_1894_', '_1899_',
                   '_1932_', '_1933_', '_1945_', '_1954_', '_1979_', '_1984_',
                   '_1989_', '_2000_', '_2001_']

# Delete these files
path = './object_detection/augmented/'
for file in generated_files:
    for num in delete_numbers:
        if num in file:
            os.remove(path + file)


# Remove these from the augmented_files_dictionary
for item in delete_numbers:
    for k in list(augmented_files_dictionary):
        if item in k:
            augmented_files_dictionary.pop(k)

# %% Move created augmented files to training and validation folders
'''
Get a random sample of 20 % of each category (floor division).
Move those files into their respective category folders in the
validation folder.
'''
# How many files are we starting with?
len(augmented_files_dictionary)  # 28320

# The augmented file dictionary has category info in the file name;
# get that value and store it in a dicitonary with the augmented file name.
augmented_cat_dict = {k: v.split('/')[0]
                      for k, v in augmented_files_dictionary.items()}

# Get a list of the categories
info = pd.read_csv('./img_scraping/item_info/all_item_info_categorized.csv')
included_categories = list(info.Cat.unique())

# Make folders in /validation/
path = './object_detection/augmented/validation/'
for cat in included_categories:
    if not os.path.exists(path + cat):
        os.makedirs(path + cat)

# Move the files
path = './object_detection/augmented/'
fails = []
random.seed(101)
for cat in included_categories:
    try:
        curr_files = [k for k, v in augmented_cat_dict.items()
                      if v == cat]
        # Get the number of files corresponding to floor of 20%
        n_files = len(curr_files)//5
        #  Get random subset of those files
        subset = random.sample(curr_files, n_files)
        # Move the files
        for file in subset:
            shutil.move(path + file,
                        os.path.join(path + '/validation/' + cat + '/' + file))
    except Exception as e:
        fails.append(e)
print(fails)  # none

# %% Now move complement set of files to /augmented/training/

# Make folders in /training/
path = './object_detection/augmented/training/'
for cat in included_categories:
    if not os.path.exists(path + cat):
        os.makedirs(path + cat)

# Move the files
path = './object_detection/augmented/'
training_files = [x for x in os.listdir(path) if not os.path.isdir(x)]
training_files = [x for x in training_files if '.DS' not in x]

# Move files to subdirectories in /training/
fails = []
for file in training_files:
    if os.path.exists(path + file):
        try:
            cat = augmented_cat_dict[file]
            shutil.move(path + file,
                        path + 'training/' + cat + '/' + file)
        except Exception as e:
            fails.append(e)
