
import cv2
import numpy as np
from skimage import color
import argparse
import colour # for delta_E calc :  pip3 install colour-science
from sklearn.cluster import KMeans
from collections import Counter



def get_dominant_color(image, k=4, image_processing_size = None):
    """
    SOURCE : https://adamspannbauer.github.io/2018/03/02/app-icon-dominant-colors/

    takes an image as input
    returns the dominant color of the image as a list

    dominant color is found by running k means on the
    pixels & returning the centroid of the largest cluster

    processing time is sped up by working with a smaller image;
    this resizing can be done with the image_processing_size param
    which takes a tuple of image dims as input

    >>> get_dominant_color(my_image, k=4, image_processing_size = (25, 25))
    [56.2423442, 34.0834233, 70.1234123]
    """
    #resize image if new dims provided
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size,
                            interpolation = cv2.INTER_AREA)

    #reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    #cluster and assign labels to the pixels
    clt = KMeans(n_clusters = k)
    labels = clt.fit_predict(image)

    #count labels to find most popular
    label_counts = Counter(labels)

    #subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return list(dominant_color)

def getLabVal(imageName):
    # read in image of interest
    bgr_image = cv2.imread(imageName)

    # convert to HSV; this is a better representation of how we see color
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

    dom_color = get_dominant_color(hsv_image, k=4, image_processing_size = (25, 25))

    # create one pixel square showing dominant color, for square of equal size to input image change 1st arg to bgr_image.shape
    dom_color_hsv = np.full((1,1,3), dom_color, dtype='uint8')

    # convert hsv to bgr color space
    dom_color_bgr = cv2.cvtColor(dom_color_hsv, cv2.COLOR_HSV2BGR)[0][0]
    color.colorconv.lab_ref_white = np.array([0.96422, 1.0, 0.82521])
    # convert bgr to lab color space
    lab = color.rgb2lab(dom_color_bgr)

    return lab

def main():
    detailedResult =False
    # construct the argument parser and parse the arguments
    ap = argparse.ArgumentParser()
    ap.add_argument("-io", "--imagePathOld", required=True,
                    help="Path to image to find dominant color of")
    ap.add_argument("-in", "--imagePathNew", required=True,
                    help="Path to image to find dominant color of")
    ap.add_argument("-k", "--clusters", default=3, type=int,
                    help="Number of clusters to use in kmeans when finding dominant color")
    args = vars(ap.parse_args())

    lab1 = getLabVal(args['imagePathOld'])
    lab2 = getLabVal(args['imagePathNew'])

    # print(lab1,lab2)

    delta_E = colour.delta_E(lab1, lab2)
    # A result less than 2 is generally considered to be perceptually equivalent.
    if(delta_E > 2):
        print("================== Test failed : the theme change is inconsistent ===================")
    else:
        print("================== Test passed : the theme is consistent ===================")

    if(detailedResult):
        print("==================DETAILED RESULT===================")
        print("If delta_E value of two images is less than 2, the images are generally considered to be perceptually equivalent.")
        print("The delta_E value for the input image is ",delta_E)

if __name__ == "__main__":
    main()
