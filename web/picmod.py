import json
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from vector_search import vector_search as vs
import annoy
from PIL import Image as PILImage
from keras.preprocessing import image
from keras.models import load_model

# Load net for SDD image segmentation CNN
ssd_cnn = cv2.dnn.readNetFromCaffe(('./model_files/SSDmodel'
                                    '/MobileNetSSD_deploy.prototxt.txt'),
                                   ('./model_files/SSDmodel'
                                    '/MobileNetSSD_deploy.caffemodel'))
# Define object classes
classes = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle",
           "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]
conf = .4 # set minimum confidence for SSD bounding box

# Load feature extraction CNN
feature_cnn = load_model('./model_files/headlessVGG16.h5')

# Load lookup files
with open('./model_files/source.json', 'r') as f:
    source = json.load(f)
with open('./model_files/item.json', 'r') as f:
    item = json.load(f)
item_info = pd.read_csv(('./model_files/all_item_info_categorized.csv'))
with open('./model_files/ref_img_filemapping.json',
          'r') as f:
    mapping = json.load(f)


ref_db = annoy.AnnoyIndex(4096, metric='angular')
ref_db.load('./model_files/ref_img_index.ann')

def get_names_cats(input_picture):
    """
    Get bottle match names and categories from input_picture
    Return: list of names and list of categories
    """
    img = input_picture
    img = cv2.imread(img)
    (h, w) = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)),
                                 0.007843, (300, 300), 127.5)

    # Run the SSD
    ssd_cnn.setInput(blob)
    detections = ssd_cnn.forward()

    # Get sliced bottles
    out_images = []
    for i in np.arange(0, detections.shape[2]):
        # extract the confidence associated with the prediction
        confidence = detections[0, 0, i, 2]

        # filter out weak detections by ensuring the confidence is
        # greater than the minimum confidence
        if confidence > conf:
            # extract the index of the class label from the `detections`,
            # then compute the (x, y)-coordinates of the bounding box for
            # the object
            idx = int(detections[0, 0, i, 1])

            # Only do this if a bottle is detected
            if idx == 5:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                box_int = box.astype('int')

                # Crop each bottle out, then save it as a separate file
                out_images.append(img[box_int[1]:box_int[3],
                                      box_int[0]:box_int[2]])

    pil_images = [cv2.cvtColor(pic, cv2.COLOR_BGR2RGB) for pic in out_images]
    pil_images = [PILImage.fromarray(pic) for pic in pil_images]

    feats = []
    for pic in pil_images:
        features = vs.generate_features_img(pic, feature_cnn)
        feats.append(features)

    # Reshape and convert to list
    feats = [x.reshape(x.shape[1]) for x in feats]
    feats = [x.tolist() for x in feats]

    match_list = []
    for pic in feats:
        (ind, dist) = vs.search_index_by_value(pic, ref_db, mapping)
        match_list.append(tuple(ind, dist))

    # Get just indices from match_list
    best_inds = [str(x[0]) for x in match_list]

    # Lookup names for best inds
    best_names = [item[x] for x in best_inds]

    best_cats = [item_info.loc[item_info['Name'] == x] for x in best_names]

    # remove redundancies
    best_names = set(best_names)
    best_cats = set(best_cats)

    return best_names, best_cats
