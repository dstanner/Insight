import os
import json

import h5py
import numpy as np

from annoy import AnnoyIndex
from keras import optimizers
from keras.layers import Dense, BatchNormalization
from keras.layers import Activation, Dropout
from keras.losses import categorical_crossentropy
from keras.preprocessing import image
from keras.models import Model
from PIL import Image as PILImage
from keras.applications.vgg16 import VGG16
from keras.applications.vgg16 import preprocess_input
import tensorflow as tf


graph = tf.get_default_graph()


def load_imgs(file_list):
    """
    Loads and preprocesses image file_list
    :return: np.array with image data
    """
    image_list = []

    for file in file_list:
        img = image.load_img(file, target_size=(224, 224))
        x_raw = image.img_to_array(img)
        x_expand = np.expand_dims(x_raw, axis=0)
        x = preprocess_input(x_expand)
        image_list.append(x)

    return image_list


def load_headless_pretrained_model():
    """
    Loads the pretrained version of VGG with the last layer cut off
    :return: pre-trained headless VGG16 Keras Model
    """
    pretrained_vgg16 = VGG16(weights='imagenet', include_top=True)
    model = Model(inputs=pretrained_vgg16.input,
                  outputs=pretrained_vgg16.get_layer('fc2').output)
    return model

def generate_features_file(image_file_list, model):
    """
    Takes in a list of image files, and a trained model.
    Returns the activations of the last layer for each image
    :param image_paths: list of image files
    :param model: pre-trained model
    :return: array of last-layer activations,
        and mapping from array_index to file_path
    """
    images = np.zeros(shape=(len(image_file_list), 224, 224, 3))
    file_mapping = {i: f for i, f in enumerate(image_file_list)}

    # We load all our dataset in memory because it is relatively small
    for i, f in enumerate(image_file_list):
        print("Loading image ",i,"/",str(len(image_file_list)))
        img = image.load_img(f, target_size=(224, 224))
        x_raw = image.img_to_array(img)
        x_expand = np.expand_dims(x_raw, axis=0)
        images[i, :, :, :] = x_expand
    print("Preprocessing images")
    inputs = preprocess_input(images)
    print("Getting features")
    images_features = model.predict(inputs)
    print("All done!")
    return images_features, file_mapping

def generate_features_img(PIL_image, model):
    """
    Takes a PIL image in memory, and a trained model.
    Returns the activations of the last layer for each image.
    :param image_array: image array already in memory
    :param model: pre-trained model
    :return: array of last-layer activations
    """
    resize = PIL_image.resize((224, 224), PILImage.NEAREST)
    x_raw = image.img_to_array(resize)
    x_expand = np.expand_dims(x_raw, axis=0)
    input = preprocess_input(x_expand)
    global graph, bike_labels
    with graph.as_default():
        images_features = model.predict(input)

    return images_features


def save_features(features_filename, features, mapping_filename, file_mapping):
    """
    Save feature array and file_item mapping to disk
    :param features_filename: path to save features to
    :param features: array of features
    :param mapping_filename: path to save mapping to
    :param file_mapping: mapping from array_index to file_path/plaintext_word
    """
    print("Saving files")
    np.save('%s.npy' % features_filename, features)
    with open('%s.json' % mapping_filename, 'w') as index_file:
        json.dump(file_mapping, index_file)


def load_features(features_filename, mapping_filename):
    """
    Loads features and file_item mapping from disk
    :param features_filename: path to load features from
    :param mapping_filename: path to load mapping from
    :return: feature array and file_item mapping to disk

    """
    images_features = np.load('%s.npy' % features_filename)
    with open('%s.json' % mapping_filename) as f:
        index_str = json.load(f)
        file_index = {int(k): str(v) for k, v in index_str.items()}
    return images_features, file_index


def index_features(features, n_trees=1000, dims=4096, is_dict=False):
    """
    Use Annoy to index our features to be able to query them rapidly
    :param features: array of item features
    :param n_trees: number of trees to use for Annoy. Higher is more precise but slower.
    :param dims: dimension of our features
    :return: an Annoy tree of indexed features
    """
    feature_index = AnnoyIndex(dims, metric='angular')
    for i, row in enumerate(features):
        print("Adding item ", i, '/', features.shape[0])
        vec = row
        if is_dict:
            vec = features[row]
        feature_index.add_item(i, vec)
    feature_index.build(n_trees)
    return feature_index

def load_annoy(filename, dims):
    '''
    Loads a pre-indexed annoy indexed database.
    '''
    a = AnnoyIndex(dims, metric='angular')
    a.load(filename)
    return a


def search_index_by_key(key, feature_index, item_mapping, top_n=1):
    """
    Search an Annoy index by key, return n nearest items
    :param key: the index of our item in our array of features
    :param feature_index: an Annoy tree of indexed features
    :param item_mapping: mapping from indices to paths/names
    :param top_n: how many items to return
    :return: an array of [index, item, distance] of size top_n
    """
    distances = feature_index.get_nns_by_item(key, top_n, include_distances=True)
    return [[a, item_mapping[a], distances[1][i]] for i, a in enumerate(distances[0])]


def search_index_by_value(vector, feature_index, item_mapping, top_n=1):
    """
    Search an Annoy index by value, return n nearest items
    :param vector: the index of our item in our array of features
    :param feature_index: an Annoy tree of indexed features
    :param item_mapping: mapping from indices to paths/names
    :param top_n: how many items to return
    :return: an array of [index, item, distance] of size top_n
    """
    distances = feature_index.get_nns_by_vector(vector, top_n, include_distances=True)
    return [[a, item_mapping[a], distances[1][i]] for i, a in enumerate(distances[0])]



def get_weighted_features(class_index, images_features):
    """
    Use class weights to re-weigh our features
    :param class_index: Which Imagenet class index to weigh our features on
    :param images_features: Unweighted features
    :return: Array of weighted activations
    """
    class_weights = get_class_weights_from_vgg()
    target_class_weights = class_weights[:, class_index]
    weighted = images_features * target_class_weights
    return weighted


def get_class_weights_from_vgg(save_weights=False, filename='class_weights'):
    """
    Get the class weights for the final predictions layer as a numpy martrix,
        and potentially save it to disk.
    :param save_weights: flag to save to disk
    :param filename: filename if we save to disc
    :return: n_classes*4096 array of weights from the penultimate layer to
        the last layer in Keras' pretrained VGG
    """
    model_weights_path = os.path.join(os.environ.get('HOME'),
                                      ('.keras/models/',
                                       'vgg16_weights_tf_dim_ordering',
                                       '_tf_kernels.h5'))
    weights_file = h5py.File(model_weights_path, 'r')
    weights_file.get('predictions').get('predictions_W_1:0')
    final_weights = weights_file.get('predictions').get('predictions_W_1:0')

    class_weights = np.array(final_weights)[:]
    weights_file.close()
    if save_weights:
        np.save('%s.npy' % filename, class_weights)
    return class_weights


def setup_custon_model(ncat):
    """
    Builds a custom model taking the fc2 layer of VGG16 and adding two dense
        layers and a final categorization layer on top.
    :param ncat: number of categories for final categorizaiton layer
    :param train_filepath: path to training pictures (organized into subfolders
        by category)
    :param validation_filepath: path to validation pictures (as above)
    :param n_train_samples: number of training images
    :param n_validation_samples: number of validation samples
    :return: a Keras model with the backbone frozen, and the upper
        layers ready to be trained
    """
    headless_pretrained_vgg16 = VGG16(weights='imagenet', include_top=True,
                                      input_shape=(224, 224, 3))
    x = headless_pretrained_vgg16.get_layer('fc2').output

    # We do not re-train VGG entirely here, just to get to a result quicker
    # (fine-tuning the whole network would lead to better results)
    for layer in headless_pretrained_vgg16.layers:
        layer.trainable = False

    # build a classifier model to put on top of the convolutional model
    image_dense1 = Dense(2000, name="image_dense1")(x)
    image_dense1 = BatchNormalization()(image_dense1)
    image_dense1 = Activation("relu")(image_dense1)
    image_dense1 = Dropout(0.5)(image_dense1)

    output = Dense(ncat, activation='softmax',
                   name='predictions')(image_dense1)

    complete_model = Model(inputs=[headless_pretrained_vgg16.input],
                           outputs=output)
    adam = optimizers.Adam()
    complete_model.compile(optimizer=adam, loss=categorical_crossentropy,
                           metrics=['accuracy'])

    return complete_model
