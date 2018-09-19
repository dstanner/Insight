import os
import shutil

totalwine = []
liquormart = []
winetoship = []

for path, directory, files in os.walk('../raw_ref_img/totalwine/'):
    for name in files:
        totalwine.append(name)
        
for path, directory, files in os.walk('../raw_ref_img/liquormart/'):
    for name in files:
        liquormart.append(name)
        
for path, directory, files in os.walk('../raw_ref_img/winetoship/'):
    for name in files:
        winetoship.append(name)


for file in totalwine:
    shutil.copy('../raw_ref_img/totalwine/' + file, '../raw_ref_img/full/totalwine_'+file)

for file in liquormart:
    shutil.copy('../raw_ref_img/liquormart/' + file, '../raw_ref_img/full/liquormart_'+file)
    
for file in winetoship:
    shutil.copy('../raw_ref_img/winetoship/' + file, '../raw_ref_img/full/winetoship_'+file)