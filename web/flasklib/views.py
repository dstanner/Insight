from flask import render_template
from flask import Flask, flash, request, redirect, url_for
from werkzeug.utils import secure_filename
from flasklib import app
import os

import json
import cv2
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from web_vector_search import vector_search as vs
from web_vector_search import model_mapping
from web_vector_search import lookup_functions
import annoy
from PIL import Image as PILImage
from keras.models import load_model
import tensorflow as tf

app.config.update(dict(
        UPLOAD_FOLDER = "./flasklib/static/uploads/",
        DISPLAY_FOLDER = "./flasklib/static/display/",
        TEMP_FOLDER = "./static/uploads/"
        ))
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


recipe_idx = 0

@app.route('/')
@app.route('/index')
def index():
    return render_template("index.html")


@app.route('/output', methods=['POST', 'GET'])
def upload_file():

    # Get the file
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            global filename
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            print(filepath)

        inds, dists, boxes = model_mapping.retrieve_img_data(filepath)

        if inds == "No match":
            cocktail_name = "I don't have any matches for your bottles."
            instructions = ("I couldn't find any good matches for the "
                            "bottle(s) in your picture in my database.\n\n"
                            "You can try uploading the picture again.\n\n"
                            "Make sure that any bottles are standing upright, "
                            "are clearly visible, "
                            "and that the labels are facing the camera.")
            ingredient_table = ""
        elif inds == "None":
            cocktail_name = "I didn't detect any bottles."
            instructions = ("I couldn't see any bottles in your picture.\n\n"
                            "You can try uploading the picture again.\n\n"
                            "Make sure that any bottles are standing upright, "
                            "are clearly visible, "
                            "and that the labels are facing the camera.")
            ingredient_table = ""
        else:
            output = lookup_functions.return_output(inds)
            global choices
            choices = lookup_functions.get_choices(output)
            recipe = lookup_functions.get_recipe(choices, recipe_idx)
            cocktail_name, instructions, ingredient_table = lookup_functions.format_recipe(recipe)

        display_path = os.path.join(app.config['TEMP_FOLDER'], filename)

    return render_template("output.html",
                           cocktail_name=cocktail_name,
                           instructions=instructions,
                           ingredient_table=ingredient_table,
                           filepath=display_path)


@app.route('/shake', methods=['POST', 'GET'])
def new_recipe():

    # update recipe index
    global recipe_idx
    recipe_idx += 1

    # Get a new recipe for that index
    recipe = lookup_functions.get_recipe(choices, recipe_idx)
    cocktail_name, instructions, ingredient_table = lookup_functions.format_recipe(recipe)

    display_path = os.path.join(app.config['TEMP_FOLDER'], filename)

    return render_template("shake.html",
                           cocktail_name=cocktail_name,
                           instructions=instructions,
                           ingredient_table=ingredient_table,
                           filepath=display_path)
