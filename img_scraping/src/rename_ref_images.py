import os
import shutil

totalwine = []
liquormart = []
winetoship = []

for path, directory, files in os.walk('./img_scraping/raw_ref_img/totalwine/'):
    for name in files:
        totalwine.append(name)

for path, directory, files in os.walk('./img_scraping/raw_ref_img/liquormart/'):
    for name in files:
        liquormart.append(name)

for path, directory, files in os.walk('./img_scraping/raw_ref_img/winetoship/'):
    for name in files:
        winetoship.append(name)


for file in totalwine:
    shutil.copy('./img_scraping/raw_ref_img/totalwine/' + file,
                './img_scraping/raw_ref_img/full/totalwine_' + file)

for file in liquormart:
    shutil.copy('./img_scraping/raw_ref_img/liquormart/' + file,
                './img_scraping/raw_ref_img/full/liquormart_' + file)

for file in winetoship:
    shutil.copy('./img_scraping/raw_ref_img/winetoship/' + file,
                './img_scraping/raw_ref_img/full/winetoship_' + file)
