import cv2
import numpy as np
import pytesseract
from sklearn.cluster import KMeans
from collections import Counter
from skimage import color
import os, sys


# from langdetect import detect_langs


def get_grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)


def get_dominant_color(image, k=4, image_processing_size=None):
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
    # resize image if new dims provided
    if image_processing_size is not None:
        image = cv2.resize(image, image_processing_size, interpolation=cv2.INTER_AREA)

    # reshape the image to be a list of pixels
    image = image.reshape((image.shape[0] * image.shape[1], 3))

    # cluster and assign labels to the pixels
    clt = KMeans(n_clusters=k)
    labels = clt.fit_predict(image)

    # count labels to find most popular
    label_counts = Counter(labels)

    # subset out most popular centroid
    dominant_color = clt.cluster_centers_[label_counts.most_common(1)[0][0]]

    return list(dominant_color)


def get_lab_val(imageName, considerKeyboard,bounds):
    # read in image of interest
    bgr_image = cv2.imread(imageName)
    if considerKeyboard:
        # croppedA = crop_keyboard(bgr_image)
        # hasKeyboard = labelPredictor.has_keyboard(croppedA)
            # print(hasKeyboard, args["first"])
        # if hasKeyboard:
        bgr_image = throw_away_keyboard(bgr_image)

    if bounds:
        bgr_image = focus_element(bgr_image,bounds)
    # convert to HSV; this is a better representation of how we see color
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

    dom_color = get_dominant_color(hsv_image, k=4, image_processing_size=(25, 25))

    # create one pixel square showing dominant color, for square of equal size to input image change 1st arg to bgr_image.shape
    dom_color_hsv = np.full((1, 1, 3), dom_color, dtype="uint8")

    # convert hsv to bgr color space
    dom_color_bgr = cv2.cvtColor(dom_color_hsv, cv2.COLOR_HSV2BGR)[0][0]

    # print(dom_color_bgr, "BGR")
    color.colorconv.lab_ref_white = np.array([0.96422, 1.0, 0.82521])
    # convert bgr to lab color space
    lab = color.rgb2lab(dom_color_bgr)

    return lab


def dominant_rgb_val(imageName):
    # read in image of interest
    bgr_image = cv2.imread(imageName)

    # convert to HSV; this is a better representation of how we see color
    hsv_image = cv2.cvtColor(bgr_image, cv2.COLOR_BGR2HSV)

    dom_color = get_dominant_color(hsv_image, k=4, image_processing_size=(25, 25))

    # create one pixel square showing dominant color, for square of equal size to input image change 1st arg to bgr_image.shape
    dom_color_hsv = np.full((1, 1, 3), dom_color, dtype="uint8")

    # convert hsv to bgr color space
    dom_color_bgr = cv2.cvtColor(dom_color_hsv, cv2.COLOR_HSV2BGR)[0][0]

    # print(dom_color_bgr, "BGR")

    return dom_color_bgr


def is_image_light(img):
    """input is 30/abc.png"""
    rgb = dominant_rgb_val(img)
    if rgb[0] <= 150 and rgb[1] <= 150 and rgb[2] <= 150:
        return "dark"
    else:
        return "light"


def read_text_on_screen(bugId, screen):
    """read text from image if no xml present"""
    """bug id like 1, screen like step["screenshot"] val"""
    screen_background = is_image_light(os.path.join(bugId, screen))
    screen_path = os.path.join(bugId, screen)
    # print(screen_background, "BACKKKK")
    text_in_screen = readTextAfterCrop(screen_path, screen_background)
    return text_in_screen


def readTextInImage(img):
    """not good if theme is dark"""
    img_cv = cv2.imread(img)
    gray = get_grayscale(img_cv)
    text = pytesseract.image_to_string(gray)
    return text


def displayImage(img):
    cv2.imshow("image window", img)

    cv2.waitKey(0)
    # and finally destroy/close all open windows
    cv2.destroyAllWindows()
    # print("GETTING HERE")


def crop_bottom_notification(img):
    screenDPI = 420  # pixel 2 used for all bugs so fixed
    sizeOfStatusBar = 25  # sizeOfStatusBar from Android Material design
    sizeOfBottomNavigationBar = 56

    y = int(sizeOfStatusBar * (screenDPI / 160))
    x = 0
    dimensions = img.shape
    height = img.shape[0]
    width = img.shape[1]
    height = height - y - int(sizeOfBottomNavigationBar * (screenDPI / 160))
    crop_img = img[y : height + y, x : x + width]

    return crop_img


def crop_keyboard(img):
    # im = Image.open(image)

    # Size of the image in pixels (size of original image)
    # width, height = im.size
    # dimensions = img.shape
    height = img.shape[0]
    width = img.shape[1]

    # resize the input to 1080*1920 if not this size originally
    if width != 1080 or height != 1920:
        newSize = (1080, 1920)
        # im = im.resize(newSize)
        img = cv2.resize(img, newSize)

    left = 5
    top = int(1920 / 2) + 150
    right = 1080
    bottom = 1920
    crop_img = img[top:bottom, left:right]

    return crop_img

    # im1 = im.crop((left, top, right, bottom))
    # return im1
    # im1.save(newImage)
def throw_away_keyboard(img):
    height = img.shape[0]
    width = img.shape[1]

    # resize the input to 1080*1920 if not this size originally
    if width != 1080 or height != 1920:
        newSize = (1080, 1920)
        # im = im.resize(newSize)
        img = cv2.resize(img, newSize)

    left = 0
    top = 0 #int(1920 / 2) + 150
    right = 1080
    bottom = int(1920 / 2) + 150
    crop_img = img[top:bottom, left:right]
    # displayImage(crop_img)
    return crop_img


def focus_element(img, bounds):
    height = img.shape[0]
    width = img.shape[1]

    # resize the input to 1080*1920 if not this size originally
    if width != 1080 or height != 1920:
        newSize = (1080, 1920)
        # im = im.resize(newSize)
        img = cv2.resize(img, newSize)

    x = bounds.split(",")
    left = int(x[0])
    top = int(x[1]) #int(1920 / 2) + 150
    right = int(x[2])
    bottom = int(x[3])#int(1920 / 2) + 150
    crop_img = img[top:bottom, left:right]
    # displayImage(crop_img)
    return crop_img

def readTextAfterCrop(img, screen_background):
    thresholdVal = (
        cv2.THRESH_BINARY_INV
    )  # assume screens are light with dark font usually

    if screen_background == "light":
        thresholdVal = cv2.THRESH_BINARY_INV

    if screen_background == "dark":
        thresholdVal = cv2.THRESH_BINARY

    # Read image from which text needs to be extracted
    img_cv = cv2.imread(img)
    img_cv = crop_bottom_notification(img_cv)

    # Preprocessing the image starts

    # Convert the image to gray scale
    gray = get_grayscale(img_cv)

    # Performing OTSU threshold changed 0 to 127
    ret, thresh1 = cv2.threshold(gray, 127, 255, cv2.THRESH_OTSU | thresholdVal)
    # thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Specify structure shape and kernel size.
    # Kernel size increases or decreases the area
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))

    # Applying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations=1)

    # Finding contours
    contours, hierarchy = cv2.findContours(
        dilation, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE
    )

    # Creating a copy of image
    im2 = gray.copy()

    # # A text file is created and flushed
    # file = open("recognized.txt", "w+")
    # file.write("")
    # file.close()
    result = []
    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)

        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)

        # Cropping the text block for giving input to OCR
        cropped = im2[y : y + h, x : x + w]

        # displayImage(cropped)

        # Open the file in append mode
        # file = open("recognized.txt", "a")

        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped).strip()
        if text != "":  # symbols are '', don't add them
            result.append(text)
        # Appending the text into file
        # file.write(text)
        # file.write("\n")

        # # Close the file
        # file.close
    return result


def main():
    img = "/Users/name/Desktop/1.png"

    print("---------GRY------")
    image = cv2.imread(img)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray_text = pytesseract.image_to_string(gray)
    # print(gray_text)

    print("-----SHRP----------")

    sharpen_kernel = np.array([[-1, -1, -1], [-1, 9, -1], [-1, -1, -1]])
    sharpen = cv2.filter2D(gray, -1, sharpen_kernel)
    shp_text = pytesseract.image_to_string(sharpen)
    print(shp_text)
    print("-----THR------BEST RESULT FOR OCR----")

    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    thr_text = pytesseract.image_to_string(thresh)
    print(thr_text)
    print("-------CLS--------")
    # Perform morpholgical operations to clean image
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    close = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel, iterations=1)
    cls_text = pytesseract.image_to_string(close)
    print(cls_text)
    print("--------RSLT-------")

    result = 255 - close
    rslt_text = pytesseract.image_to_string(result)
    print(rslt_text)

    print("---------------")

    cv2.imshow("sharpen", sharpen)
    cv2.imshow("thresh", thresh)
    cv2.imshow("close", close)
    cv2.imshow("result", result)
    cv2.waitKey()


if __name__ == "__main__":
    main()
