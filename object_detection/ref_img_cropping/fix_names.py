"""
Correct the file names for the reference images to match
the image type.abs

Then convert all images to PNG format.
"""


import imghdr
import os
import re
from PIL import Image

folder = './object_detection/ref_img_cropping/raw_images/'

# Get list of image files
image_list = os.listdir(folder)
image_list = [x for x in image_list if '.DS_Store' not in x]
image_list = [folder + x for x in image_list]


# Fix file suffixes on files first; get correct image type
img_types = [imghdr.what(x) for x in image_list]
img_types = [x.replace('jpeg', 'jpg') for x in img_types]
strip_ext = [re.sub('(.jpg|.jpeg|.png|.gif)', '', x) for x in image_list]

new_names = []

# Get new file names
for i in range(len(strip_ext)):
    new_names.append(strip_ext[i] + '.'  + img_types[i])

for i in range(len(image_list)):
    os.rename(image_list[i], new_names[i])

# Now convert all images to png
for img in new_names:
    name = img.replace('(jpg|jpeg|png|gif)', 'png')
    curr = Image.open(img)
    curr.save(name, "PNG")
