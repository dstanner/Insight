#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 21:18:47 2018

@author: Darren
"""

# import the necessary packages
import numpy as np
import cv2
from matplotlib import pyplot as plt
import os
import sys
import pandas as pd

fails = []

plt.ioff()  # turn off interactive mode for image processing

os.chdir('/Users/Darren/Documents/GitHub/Insight/' +
         'object_detection/ref_img_cropping')

# Set confidence level for retaining bounding box
conf = .4

# initialize the list of class labels MobileNet SSD was trained to
# detect, then generate a set of bounding box colors for each class
classes = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle",
           "bus", "car", "cat", "chair", "cow", "diningtable",
           "dog", "horse", "motorbike", "person", "pottedplant", "sheep",
           "sofa", "train", "tvmonitor"]

# load our serialized model from disk
net = cv2.dnn.readNetFromCaffe('./model/MobileNetSSD_deploy.prototxt.txt',
                               './model/MobileNetSSD_deploy.caffemodel')

# Get list of image files
image_list = os.listdir('./raw_images/')
image_list = [x for x in image_list if '.DS_Store' not in x]
image_list = ['./raw_images/' + x for x in image_list]

# Loop over images.
# First resize to a fixed 300x300 pixels and then normalizing it
# (note: normalization is done via the authors of the MobileNet SSD
# implementation)

for ind, img in enumerate(image_list):
    print('Processing image ', str(ind+1))

    try:
        picname = img.replace('./raw_images/', '')
        image = plt.imread(img)
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)),
                                     0.007843, (300, 300), 127.5)

        # pass the blob through the network and obtain the detections and
        # predictions
        net.setInput(blob)
        detections = net.forward()

        plt.figure(figsize=(16, 10))
        plt.imshow(image)

        current_axis = plt.gca()

        # loop over the detections
        for i in np.arange(0, detections.shape[2]):
            # extract the confidence (i.e., probability) associated with the
            # prediction
            confidence = detections[0, 0, i, 2]

            # filter out weak detections by ensuring the `confidence` is
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
                    new_image = image[box_int[1]:box_int[3],
                                      box_int[0]:box_int[2]]
                    new_filename = ('./cropped_images/crop_' +
                                    str(i) + '_' + picname)
                    plt.imsave(new_filename, new_image)

                    # display the prediction
                    color = (1, 0, 0, 1)
                    label = "{}: {:.2f}%".format(classes[idx], confidence)
                    current_axis.add_patch(plt.Rectangle((box_int[0],
                                                          box_int[1]),
                                                         box_int[2]-box_int[0],
                                                         box_int[3]-box_int[1],
                                                         color=color,
                                                         fill=False,
                                                         linewidth=2))
                    current_axis.text(box_int[0], box_int[1], label,
                                      size='x-large',
                                      color='white',
                                      bbox={'facecolor': color, 'alpha': 1.0})

        out_img = plt.gcf()
        plt.close('all')
        out_img.savefig('./bounded_images/' + picname + '.png')

    except Exception as e:
        tp, val, tb = sys.exc_info()
        ex_dict = {'image': img, 'Type': tp, 'value': val, 'traceback': tb}
        fails.append(ex_dict)

fails_df = pd.DataFrame(fails)
fails_df.to_csv("cropping_fails.csv", index=False)

# %%

fails_df = pd.read_csv("cropping_fails.csv")
