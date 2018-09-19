#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Sep 13 13:22:02 2018

Scrape liquor store images and bottle metadata

@author: Darren
"""

from bs4 import BeautifulSoup
import requests
import time
from textwrap import dedent
import pandas as pd
from random import randint
import sys

def remove_newline(list):
    list = [item.replace('\n', '') for item in list]
    return list


#%% Make a list of URLs to extract hrefs from from totalwine.com
totalwine_base_url = 'https://www.totalwine.com/spirits/c/c0030?tab=fullcatalog&viewall=true&text=&pagesize=180&page='
totalwine_p_num = 86

page_url_list = [totalwine_base_url+str(i) for i in range(1, totalwine_p_num+1)]

# Query the pages to get item urls
totalwine_item_urls = []

totalwine_add_prefix = 'https://www.totalwine.com/'

for page in page_url_list:
    
    # Load the current page
    curr = requests.get(page).content
    curr = BeautifulSoup(curr, 'lxml')
    
    # Get the stuff from the page and appnd it to the output container
    for item in curr.find_all(attrs={'class': 'plp-list-product-img'}):
        for link in item.find_all('a'):
            totalwine_item_urls.append(link.get('href'))
            
    time.sleep(7)

totalwine_complete_item_urls = [totalwine_add_prefix + url for url in totalwine_item_urls]

# Get rid of duplicaes
totalwine_item_urls = list(set(totalwine_complete_item_urls))

# Get rid of bot checker
totalwine_item_urls = [x.replace('&igrules=true', '') for x in totalwine_item_urls]

with open("../urls/totalwine_item_urls.txt", "w") as f:
    for item in totalwine_item_urls:
        f.write('%s\n' % item)

#%% Get info from totalwine image urls

totalwine_img_urls['img_url'].nunique()

totalwine_img_urls['img_url'].value_counts()

'''
Values to skip:
    https://www.totalwine.com//media/sys_master/twmmedia/ha2/h31/8824572280862.png
    https://www.totalwine.com/Unavailable
    https://www.totalwine.com/ 
'''
        

#%% Now get image urls from totalwine

with open("../urls/totalwine_item_urls.txt", 'r') as y:
    totalwine_item_urls = y.readlines()
    
# Get rid of nl character
totalwine_item_urls = remove_newline(totalwine_item_urls) 


# Initialize output
totalwine_image_urls = [] 

# Scrape data
for page in totalwine_item_urls:
    
    curr_dict = dict()
    
    try:
        # Load the current page
        curr = requests.get(page)
        curr = curr.content
        curr = BeautifulSoup(curr, 'lxml')
        
        # Get the the image url and retain the item url
        container = curr.find(class_ = ['pdp-img-zoom-modal-zoom-reset', 'anPDPImage'])
        curr_dict['img_url'] = container.get('large-src')
        curr_dict['item_url'] = page
        
    except:
        # Just return the item url, with the image url as "Unavailable"
        curr_dict['img_url'] = 'Unavailable'
        curr_dict['item_url'] = page
    
    # Append to output list
    totalwine_image_urls.append(curr_dict)
    
    # Don't piss off the website!
    time.sleep(randint(2, 5))

totalwine_img_urls = pd.DataFrame(totalwine_image_urls)

totalwine_img_urls['img_url'] = 'https://www.totalwine.com/' + totalwine_img_urls['img_url'].astype(str)

totalwine_img_urls.to_csv('../urls/totalwine_image_urls.csv', index = False)

#%% Get metadata from totalwine

with open('../urls/totalwine_item_urls.txt', 'r') as f:
    totalwine_item_urls = f.readlines()

# Get rid of nl character
totalwine_item_urls = remove_newline(totalwine_item_urls) 

info = []

# name class = product-name
# name field to get = value
# Category class = analyticsProductType

for item in totalwine_item_urls:
    
    try:
        curr_info = dict()
        
        curr = requests.get(item)
        curr = curr.content
        curr = BeautifulSoup(curr, 'lxml')
        
        curr_info['Name'] = dedent(curr.find(class_ = 'product-name').text)
        curr_info['Category'] = dedent(curr.find(class_ = \
                 'analyticsProductType').text)
        curr_info['url'] = item
    
        info.append(curr_info)
        
    except:
        curr_info = dict()
        
        curr_info['Name'] = 'Unavailable'
        curr_info['Category'] = 'Unavailable'
        curr_info['url'] = item
        
        info.append(curr_info)
    
    # Don't anger the website!
    time.sleep(randint(2, 5))

# Replaces spaces with underscores in names
info['Name'] = info['Name'].str.replace(' ', '_')

item_data = pd.DataFrame(info)

item_data.to_csv('../item_info/totalwine_info.csv', index = False)

#%% Get totalwine images

totalwine_image_urls = pd.read_csv('../urls/totalwine_image_urls.csv')

totalwine_item_data = pd.read_csv('../item_info/totalwine_info.csv')

totalwine_item_data['Name'] = totalwine_item_data['Name'].str.replace(' ', '_')

totalwine_skip_urls = ['https://www.totalwine.com//media/sys_master/twmmedia/ha2/h31/8824572280862.png',
                       'https://www.totalwine.com/Unavailable',
                       'https://www.totalwine.com/']
image_failed = []


# Get pictures
for i in range(len(totalwine_image_urls)):     
    
    if totalwine_image_urls['img_url'].iloc[i] not in totalwine_skip_urls: 
        
        try:
            img_data = requests.get(totalwine_image_urls['img_url'].iloc[i]).content
            product_url = totalwine_item_data['url'].iloc[i]
            name = totalwine_item_data['Name'].iloc[i]
            filename = '../raw_ref_img/totalwine/' + name + '.png'
            with open(filename, 'wb') as img:
                img.write(img_data)
        
        except Exception as e:
            tp, val, tb = sys.exc_info()
            ex_dict = {'Name': totalwine_item_data['Name'].iloc[i],
                      'img_url': totalwine_image_urls['img_url'].iloc[i],
                      'Type': tp,
                      'value': val,
                      'traceback': tb}
            image_failed.append(ex_dict)
                
        time.sleep(randint(2,5))
        
    else:
        continue

totalwine_image_exceptions = pd.DataFrame(image_failed)


#%% I shut Totalwine.com down, so try liquormart.com

liquormart_base_url = 'https://www.liquormart.com/liquor?limit=100&p='
liquormart_n_pages = 11
liquormart_page_url_list = [liquormart_base_url+str(i) for i in range(1, liquormart_n_pages+1)]

liquormart_item_urls = []


for page in liquormart_page_url_list:
    
    # Load the current page
    curr = requests.get(page)
    curr = curr.content
    curr = BeautifulSoup(curr, 'lxml')
    
    # Get the stuff from the page and appnd it to item_urls
    for item in curr.find_all(attrs={'class': 'product-name'}):
        for link in item.find_all('a'):
            liquormart_item_urls.append(link.get('href'))
            
    # Don't shut down the domain this time
    time.sleep(3)
    
liquormart_item_urls_out = list(set(liquormart_item_urls))
liquormart_item_urls = remove_newline(liquormart_item_urls_out)

with open("../urls/liquormart_item_urls.txt", "w") as f:
    for item in liquormart_item_urls:
        f.write('%s\n' % item)
    
#%% Get image url for each item from liquormart

with open('../urls/liquormart_item_urls.txt', 'r') as f:
    liquormart_item_urls = f.readlines()

liquormart_item_urls = remove_newline(liquormart_item_urls)


liquormart_image_urls = []

for page in liquormart_item_urls:
    
    curr_info = dict()
    
    try:
        # Load the current page
        curr = requests.get(page)
        curr = curr.content
        curr = BeautifulSoup(curr, 'lxml')
        
        # Get the stuff from the page and add it to our dictionary
        curr_info['img_url'] = curr.find(attrs={'id': 'product_addtocart_form'}).find('img').get('src')
        curr_info['item_url'] = page
    
    except:
        curr_info['img_url'] = 'Unavailable'
        curr_info['item_url'] = page
    
    liquormart_image_urls.append(curr_info)
    
    # Don't piss off the website!
    time.sleep(2)

liquormart_img_urls = pd.DataFrame(liquormart_image_urls)

liquormart_img_urls.to_csv('../urls/liquormart_image_urls.csv', index = False)
        
        
#%% Get liquormart item info/metadata
        
with open('../urls/liquormart_item_urls.txt', 'r') as f:
    liquormart_item_urls = f.readlines()
liquormart_item_urls = remove_newline(liquormart_item_urls)

info = []

for item in liquormart_item_urls:
    
    curr_info = dict()
    
    curr = requests.get(item)
    curr = curr.content
    curr = BeautifulSoup(curr, 'lxml')
    
    try:
        curr_info['Name'] = dedent(curr.find('h1').text)
        curr_info['Category'] = dedent(curr.find(id = 'product-attribute-specs-table')('tr')[-1].find('td').text)
        curr_info['url'] = item
    except:
        curr_info['Name'] = dedent(curr.find('h1').text)
        curr_info['Category'] = 'Unavailable'
        curr_info['url'] = item
        
    info.append(curr_info)
    
    # Don't anger the website!
    time.sleep(randint(2,4))


item_data = pd.DataFrame(info)

item_data.to_csv('../item_info/liquormart_info.csv', index = False)

#%% Get liquormart images

liquormart_item_info = pd.read_csv('../item_info/liquormart_info.csv')
liquormart_img_urls = pd.read_csv('../urls/liquormart_image_urls.csv')

skip_url = 'https://www.liquormart.com/media/catalog/product/cache/1/image/364x/9df78eab33525d08d6e5fb8d27136e95/placeholder/default/placeholder_1.jpg'

image_failed = []

for i in range(liquormart_img_urls.shape[0]):
    
    if liquormart_img_urls['img_url'].iloc[i] != skip_url:
        try:
            name = liquormart_item_info['Name'].iloc[i].replace(" ", "_").replace('/', '_')
            
            img_data = requests.get(liquormart_img_urls['img_url'].iloc[i]).content
            
            filename = '../raw_ref_img/liquormart/' + name + '.jpg'
            with open(filename, 'wb') as img:
                img.write(img_data)
                
        except Exception as e:
            tp, val, tb = sys.exc_info()
            ex_dict = {'Name': totalwine_item_data['Name'].iloc[i],
                      'img_url': totalwine_image_urls['img_url'].iloc[i],
                      'Type': tp,
                      'value': val,
                      'traceback': tb}
            image_failed.append(ex_dict)
    
    else:
        continue
            
        time.sleep(randint(2,5))
        
## None failed, so not saving exceptions list

#%% Get data from winetoship.com
        
winetoship_base_url = 'https://www.winetoship.com/spirits/?limit=36&p='

winetoship_p_num = 90

winetoship_page_url_list = [winetoship_base_url+str(i) for i in range(1, winetoship_p_num+1)]

winetoship_image_urls = []
winetoship_item_pages = []
winetoship_item_names = []

for page in winetoship_page_url_list:
    
    # Load the current page
    curr = requests.get(page)
    curr = curr.content
    curr = BeautifulSoup(curr, 'lxml')

    # Get image urls    
    for item in curr.find_all(class_='product-image'):
        for link in item.find_all('img'):
            winetoship_image_urls.append(link.get('src'))
            
    # Get item pages and names
    for item in curr.find_all(class_='product-name'):
        for link in item.find_all('a'):
            winetoship_item_pages.append(link.get('href'))
            winetoship_item_names.append(link.get('title'))
        
    # Don't shut down the domain this time
    time.sleep(3)

winetoship_item_names = [item.replace(' ', '_').replace('/', '_') \
                         for item in winetoship_item_names]

winetoship_urls = pd.DataFrame(
        {'item_name': winetoship_item_names, 
         'item_url': winetoship_item_pages,
         'image_url': winetoship_image_urls})
    
winetoship_urls.to_csv('../urls/winetoship_urls.csv', index = False)


#%% Winetoship images

winetoship_urls = pd.read_csv('../urls/winetoship_urls.csv')

skip_url = 'https://www.winetoship.com/media/catalog/product/cache/1/small_image/295x295/9df78eab33525d08d6e5fb8d27136e95/placeholder/default/create_thumb_1.png'

image_failed = []

for i in range(winetoship_urls.shape[0]):
    
    if winetoship_urls['image_url'].iloc[i] != skip_url:
        
        try:
            name = winetoship_urls['item_name'].iloc[i].replace(" ", "_").replace('/', '_')
            
            img_data = requests.get(winetoship_urls['image_url'].iloc[i]).content
            
            filename = '../raw_ref_img/winetoship/' + name + '.jpg'
            with open(filename, 'wb') as img:
                img.write(img_data)
            
        except Exception as e:
            tp, val, tb = sys.exc_info()
            ex_dict = {'Name': totalwine_item_data['Name'].iloc[i],
                      'img_url': totalwine_image_urls['img_url'].iloc[i],
                      'Type': tp,
                      'value': val,
                      'traceback': tb}
            image_failed.append(ex_dict)
            
    else:
        continue
            
        time.sleep(randint(2,4))

## None failed

#%% Winetoship metadata

winetoship_urls = pd.read_csv('../urls/winetoship_urls.csv')

info = []

for i in range(winetoship_urls.shape[0]):
    
    curr_info = dict()
    
    curr = requests.get(winetoship_urls['item_url'].iloc[i])
    curr = curr.content
    curr = BeautifulSoup(curr, 'lxml')
    
    try:
        curr_info['Name'] = winetoship_urls['item_name'].iloc[i]
        curr_info['Category'] = dedent(curr.find(class_='iteminfocat', string = "Type:").find_next_sibling().text)
        curr_info['url'] = winetoship_urls['item_url'].iloc[i]
    except:
        curr_info['Name'] = winetoship_urls['item_name'].iloc[i]
        curr_info['Category'] = 'Unavailable'
        curr_info['url'] = winetoship_urls['item_name'].iloc[i]
        
    info.append(curr_info)
    
    # Don't anger the website!
    time.sleep(randint(2,4))

winetoship_info = pd.DataFrame(info)

winetoship_info.to_csv('../item_info/winetoship_info.csv', index = False)
