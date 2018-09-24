"""
Correct the file names for the reference images to match
the image type.abs

Then convert all images to JPG format.
"""
import imghdr
import os
import re
from PIL import Image

src_folder = './img_scraping/raw_ref_img/full/'
dst1_folder = './object_detection/ref_img_cropping/raw_images/'

# Get list of image files
image_list = os.listdir(src_folder)
image_list = [x for x in image_list if '.DS_Store' not in x]
source_image_list = [src_folder + x for x in image_list]
dst1_image_list = [dst1_folder + x for x in image_list]

# Fix file suffixes on files first; get correct image type
img_types = [imghdr.what(x) for x in source_image_list]
img_types = [x.replace('jpeg', 'jpg') for x in img_types]
strip_ext = [re.sub('(.jpg|.jpeg|.png|.gif)', '', x) for x in dst1_image_list]

# Get new file names for raw folder
new_names = []
for i in range(len(strip_ext)):
    new_names.append(strip_ext[i] + '.'  + img_types[i])

# Copy files to raw folder and change file names
for i in range(len(image_list)):
    print('Processing image ' + str(i+1))
    os.rename(source_image_list[i], new_names[i])

# Get file names for conversion folder
final_names = ['./object_detection/ref_img_cropping/converted_images/' + x
               for x in image_list]
final_names = [re.sub('(gif|jpg|jpeg|png)', 'png', x) for x in final_names]

# Now convert all images to jpg
for ind, img in enumerate(new_names):
    print("Processing image " + str(ind + 1))
    name = final_names[ind]

    curr = Image.open(img).convert('RGBA')
    curr.load()
    background = Image.new('RGBA', curr.size, (255,255,255))
    background.paste(curr, mask=curr.split()[3])
    background.save(name, "PNG")
