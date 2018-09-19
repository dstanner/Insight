#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 12:39:53 2018

@author: Darren
"""

from google_images_download import google_images_download   #importing the library
import selenium

response = google_images_download.googleimagesdownload()   #class instantiation

#creating list of arguments
arguments = {"keywords":"liquor bottles, booze bottles,"+\
             "liquor collection, vodka bottles, whiskey bottles, gin bottles," +\
             "rum bottles, schnapps bottles, liqueur bottles",\
             "limit":1000,\
             "output_directory":\
             "/Users/Darren/Documents/GitHub/Insight/img_scraping/messy_image_scraping",\
             "chromedriver":"/Users/Darren/Applications/Utilities/chromedriver"}   

#passing the arguments to the function
paths = response.download(arguments) 
