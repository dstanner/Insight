from vector_search import vector_search
import os
import re
import annoy

# Get images to load
ref_img_folder = './object_detection/ref_img_cropping/cropped_images/'
ref_img_files = [ref_img_folder + x for x in os.listdir(ref_img_folder)
                 if '.DS' not in x]

# Load the VGG16 model without softmax layer
model = vector_search.load_headless_pretrained_model()

# %%
# Extract features and file mappings and save them to disk
features, file_mapping = vector_search.generate_features(ref_img_files, model)

vector_search.save_features(('./object_detection/feature_extraction/'
                             'ref_img_features'),
                            features,
                            ('./object_detection/feature_extraction'
                             '/ref_img_filemapping'),
                            file_mapping)

# %%
# Load the saved features and file mappings and compile Annoy search
features, file_index = vector_search.load_features(
    'object_detection/feature_extraction/ref_img_features',
    './object_detection/feature_extraction/ref_img_filemapping')

img_index = vector_search.index_features(features, n_trees=2000)


# get image sources and description from filename
srcs = ['liquormart', 'winetoship', 'totalwine']
source = {}
for ind, file in enumerate(ref_img_files):
    for s in srcs:
        if s in file:
            source[ind] = s

item = {}
for ind, file in enumerate(ref_img_files):
    item[ind] = re.sub('./object_detection/ref_img_cropping/' +
                         'cropped_images/crop_[\d]_' +
                         '(liquormart|winetoship|totalwine)_',
                        "", file)
