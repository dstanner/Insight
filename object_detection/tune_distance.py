import os
import pandas as pd
import matplotlib.pyplot as plt
from vector_search import vector_search as vs
import json
import numpy as np
from scipy.spatial.distance import cosine
import re
from sklearn.metrics import classification_report

# Get list of augmented files and mapping dictionary, load other files

with open('./object_detection/augmented_file_list.txt', 'r') as f:
    augmented_list = f.readlines()
augmented_list = [x.replace('\n','') for x in augmented_list]

with open('./object_detection/augmented_file_mapping.json', 'r') as f:
    file_mapping = json.load(f)

model = vs.load_headless_pretrained_model()

annoy = vs.load_annoy('./object_detection/feature_extraction/ref_img_index_no_aug.ann', 4096)

with open('./object_detection/feature_extraction/ref_img_filemapping_no_aug.json', 'r') as f:
    mapping = json.load(f)


# %% Get best matches and distances

load_list = ['./object_detection/augmented/' + x for x in augmented_list]

feats, mapping = vs.generate_features_file(load_list, model)


inds = []
dists = []

for i, file in enumerate(feats):
    print("Getting item " + str(i+1) + '/' + str(len(feats)))
    idx, dist = annoy.get_nns_by_vector(file, 1, include_distances = True)
    inds.append(idx)
    dists.append(dist)

# Write to disk, first flatten lists
inds_flat = [item for sublist in inds for item in sublist]
with open('./object_detection/augmented_annoy_index_results.txt', 'w') as f:
    for item in inds_flat:
        f.write(str(item)+ '\n')

dists_flat = [item for sublist in dists for item in sublist]
with open('./object_detection/augmented_annoy_distance_results.txt', 'w') as f:
    for item in dists_flat:
        f.write(str(item) + '\n')

# %% Now wrangle data

with open('object_detection/augmented_annoy_index_results.txt', 'r') as f:
    annoy_index_results = f.readlines()
annoy_index_results = [x.replace('\n', '') for x in annoy_index_results]
annoy_index_results

with open('object_detection/augmented_annoy_distance_results.txt', 'r') as f:
    annoy_distance_results = f.readlines()
annoy_distance_results = [x.replace('\n', '') for x in annoy_distance_results]

with open('object_detection/augmented_file_list.txt', 'r') as f:
    augmented_file_list = f.readlines()
augmented_file_list = [x.replace('\n', '') for x in augmented_file_list]

with open('object_detection/augmenter_original_file_list.txt', 'r') as f:
    original_file_list = f.readlines()
original_file_list = [x.replace('\n', '') for x in original_file_list]

original_index_vector = list(range(len(original_file_list)))

full_index_vector = np.repeat(original_index_vector, 3)

df = pd.DataFrame({"Agumented_file":augmented_file_list,
                   "Distance": annoy_distance_results,
                   "Predicted_Index": annoy_index_results,
                   "Original_Index": full_index_vector})

df.to_csv('./object_detection/annoy_results.csv', index = False)

# %% Get distnace between generated image and seed image

# Get augmented image features
augmented_list = ['./object_detection/augmented/' + x for
                       x in augmented_list]

aug_img_features, aug_img_filemapping = vs.generate_features_file(
    augmented_list, model)

# Save them before anything awful happens!
np.save('./object_detection/feature_extraction/augmented_image_features.npy',
        aug_img_features)
with open('./object_detection/feature_extraction/augmented_image_filemapping.json', 'w') as f:
    json.dump(aug_img_filemapping, f)

# %% Get distances between augmented and seed images

ref_img_features = np.load('./object_detection/feature_extraction/ref_img_features_no_aug.npy')

with open('./object_detection/feature_extraction/ref_img_filemapping_no_aug.json', 'r') as f:
    ref_img_filemapping = json.load(f)
ref_img_filemapping = [x.replace('\n','') for x in ref_img_filemapping]

with open('./object_detection/augmented_file_list.txt', 'r') as f:
    augmented_list = f.readlines()
augmented_list = [x.replace('\n','') for x in augmented_list]


# Get the seed/reference index for each augmented image from its file prefix
ref_inds = [x.split('_')[1] for x in augmented_list]


cos_dist = []
for ind in range(aug_img_features.shape[0]):
    reference_index = int(ref_inds[ind])
    reference_feats = ref_img_features[reference_index]
    aug_feats = aug_img_features[ind]
    cos = cosine(reference_feats, aug_feats)
    cos_dist.append(cos)

np.savetxt('./object_detection/feature_extraction/aug_ref_cos_distance.txt', cos_dist)

# Get the categories returned from each image
with open('object_detection/pic_lookup_dictionary.json', 'r') as f:
    pic_lookup = json.load(f)

with open('object_detection/augmented_annoy_index_results.txt', 'r') as f:
    augmented_index_results = f.readlines()
augmented_index_results = [x.replace('\n', '') for x in augmented_index_results]
augmented_index_results

augmented_ref_correspondence = []
for result in augmented_index_results:
    augmented_ref_correspondence.append(mapping[result])

augmented_ref_correspondence_trunc = [x.split('/')[-1] for x in augmented_ref_correspondence]
augmented_ref_correspondence_trunc= [re.sub('(.png)', '', x) for x in augmented_ref_correspondence_trunc]
augmented_ref_correspondence_trunc

augmented_category_results = []
for x in augmented_ref_correspondence_trunc:
    augmented_category_results.append(pic_lookup[x])

with open('./object_detection/augmented_category_results.txt', 'w') as f:
    '\n'.join(augmented_category_results)
augmented_nums = [x.split('_')[1] for x in augmented_list]
augmented_expected_corr = []
for num in augmented_nums:
    augmented_expected_corr.append(mapping[num])

augmented_expected_corr = [x.split('/')[-1] for x in augmented_expected_corr]
augmented_expected_corr = [re.sub('(.jpg|.png|.jpeg)', '', x) for x in augmented_expected_corr]

augmented_expected_categories = []
for x in augmented_expected_corr:
    augmented_expected_categories.append(pic_lookup[x])

augmented_expected_categories

# Get classification metrics from sklearn as dict
metrics = classification_report(augmented_expected_categories,
                                augmented_category_results)

print(metrics)
