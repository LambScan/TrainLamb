import os
import numpy as np
import cv2

parent_folder = os.path.dirname(os.getcwd())
joinpath = os.path.join
h = 480
w = 640


def get_items_in_dir(my_path=""):
    """ Get all of file paths of the given folder path
    :param my_path: path of the folder where it will be searching
    :return: list of string with each path of the files.
    """
    my_path = os.getcwd() if my_path == "" or my_path is None else my_path
    files = []
    for roots, dirs, items in os.walk(my_path):
        [files.append(os.path.join(roots, item)) for item in items]
    return files


def load_image(filepath):
    """ Load a image composed for a couple of files (RGB and depth) both in PNG format.
    the path must be similar to each location of the files
    :param filepath: path with the RGB image file in PNG format
    :return numpy array image with (480, 640, 4) shape.
    """
    color_image = cv2.imread(filepath)
    depth_image = cv2.imread(filepath.replace("color", "depth"), cv2.IMREAD_ANYCOLOR | cv2.IMREAD_ANYDEPTH)
    return np.dstack((color_image, depth_image))


def make_YTrain(filepath):
    """ Get the expected result for a given image.
    :param filepath : file path of the image
    :return list for a given file path with the expected result of the neural network:
        [1, 0, 0] : There is a lamb in a right position
        [0, 1, 0] : There is an error in the image, or the lamb is not in a right position
        [0, 0, 1] : There is not any lamb in the image. """
    if "/lamb/" in filepath:
        return [1, 0, 0]
    elif "error" in filepath:
        return [0, 1, 0]
    else:
        return [0, 0, 1]


def get_XTrain(depth=True):
    """ Get a tuple of lists with the XTrain matrix and YTrain matrix of the dataset for the neural network.
    :param depth: bool. Get images in RGBD format (numpy array with (480, 640, 4) shape) if True.
    and RGB format (numpy array with (480, 640, 3) shape) if False.
    :return: tuple of lists (xtrain, ytrain)
        xtrain: list of images. Images in numpy array format ((480, 640, 4) or (480, 640, 3) shapes)
        ytrain: list of expected results. Results in list format (length = 3; 3 possible values (lamb, error, no_lamb))
    """
    itemlist = filter(lambda x: ".png" in x, get_items_in_dir(joinpath(parent_folder, "savings", "color")))
    np.random.shuffle(itemlist)
    xtrain = map(lambda x: load_image(x), itemlist) if depth else map(lambda x: cv2.imread(x), itemlist)
    ytrain = map(lambda x: make_YTrain(x), itemlist)

    return xtrain, ytrain


if __name__ == '__main__':
    get_XTrain(depth=True)
