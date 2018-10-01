import json
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from web_vector_search import vector_search as vs
from web_vector_search import lookup_functions
import annoy
from PIL import Image as PILImage
from keras.models import load_model
from keras.applications.vgg16 import preprocess_input
from keras.preprocessing import image
import tensorflow as tf

# %% Load CNNs

# Load net for SDD image segmentation
ssd_cnn = cv2.dnn.readNetFromCaffe(('./model_files/SSDmodel'
                                    '/MobileNetSSD_deploy.prototxt.txt'),
                                   ('./model_files/SSDmodel/MobileNetSSD_deploy.caffemodel'))
classes = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle",
           "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

conf = .5  # set minimum confidence for SSD bounding box
max_dist = .8 # Maximum cosine distance tolerance to return a match

feature_cnn = vs.load_headless_pretrained_model()

# %% Load lookup dictionary and file mapping
with open('./model_files/ref_img_filemapping_no_aug.json', 'r') as f:
    mapping = json.load(f)

# %% Load annoy database

ref_db = annoy.AnnoyIndex(4096, metric='angular')
ref_db.load('./model_files/ref_img_index_no_aug.ann')


def retrieve_img_data(file):

    # Define, load, preprocess, extract bottles

    img = cv2.imread(file)
    (h, w) = img.shape[:2]
    blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)),
                                 0.007843, (300, 300), 127.5)
    # Run the SSD
    ssd_cnn.setInput(blob)
    detections = ssd_cnn.forward()

    # Get sliced bottles and save bounding boxes
    out_images = []
    bboxes = []
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

                if box_int[0] < 0:
                    box_int[0] = 0
                if box_int[1] < 0:
                    box_int[1] = 0
                if box_int[2] > w:
                    box_int[2] = w
                if box_int[3] > h:
                    box_int[3] = h

                # Crop each bottle out, then save it as a separate file
                out_images.append(img[box_int[1]:box_int[3],
                                      box_int[0]:box_int[2]])

                # Save bounding boxes for each bottle detected
                bboxes.append(box_int)


    try:
        # %% Get features of sliced bottles
        if len(out_images) > 0:

            # Convert output to PIL
            pil_images = [cv2.cvtColor(pic, cv2.COLOR_BGR2RGB) for pic in out_images]
            pil_images = [PILImage.fromarray(pic) for pic in pil_images]

            feats = []
            for pic in pil_images:
                features = vs.generate_features_img(pic, feature_cnn)
                feats.append(features)

            # Reshape and convert to list
            feats = [x.reshape(x.shape[1]) for x in feats]
            feats = [x.tolist() for x in feats]

            # %% Get annoy result
            get_inds = []
            dists = []
            for x in feats:
                ind, dist = ref_db.get_nns_by_vector(x, 1,
                                                     include_distances = True)
                get_inds.extend(ind)
                dists.extend(dist)

            # Check distances to see if they exceed the max tolerance

            # Get indices of bad matches
            bad_matches = []
            for i, d in enumerate(dists):
                if d > max_dist:
                    bad_matches.append(i)

            # Get rid of bad matches
            inds = []
            for i, idx in enumerate(get_inds):
                if i in bad_matches:
                    continue
                else:
                    inds.append(idx)

            if len(inds) == 0:
                inds = "No match"
                dists = []
                bboxes = []


        else:
            inds = "None"
            dists = []
            bboxes = []

        return inds, dists, bboxes

    except Exception as e:
        inds = "None"
        dists = []
        bboxes = []

        return inds, dists, bboxes
