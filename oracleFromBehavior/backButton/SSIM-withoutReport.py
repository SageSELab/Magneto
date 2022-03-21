from posixpath import splitext
from pydoc import splitdoc
from skimage.metrics import structural_similarity as compare_ssim
import argparse
import imutils
import cv2
import json
import os, sys
from pathlib import Path


# Location of imageUtilities.py
scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)

import imageUtilities as imgUtil
import labelPredictor


# to display detailed result to developer
detailed_result = True
tracePlayerGenerated = True


def read_json(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def load_arguments():
    """construct the argument parse and parse the arguments"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--appName", required=True, help="second")
    ap.add_argument("-b", "--bugId", required=True, help="first input image")

    args = vars(ap.parse_args())
    return args


def crop_image(args, trigger, i):
    """load the two input images and crop their status and bottom navigation bar"""
    try:
        # print(args)
        imageA = cv2.imread(args["first"])
        croppedA = imgUtil.crop_keyboard(imageA)
        hasKeyboard = labelPredictor.has_keyboard(croppedA)
        # print(hasKeyboard, args["first"])
        if hasKeyboard:
            imageName = get_image_before(args, "first")
            imageA = cv2.imread(imageName)

        imageA = imgUtil.crop_bottom_notification(imageA)

    except Exception:
        print(args["first"] + " Image file not found")
        return

    try:
        imageB = cv2.imread(args["second"])
        croppedB = imgUtil.crop_keyboard(imageB)
        hasKeyboard = labelPredictor.has_keyboard(croppedB)
        if hasKeyboard:
            imageName = get_image_before(args, "second")
            imageB = cv2.imread(imageName)

        imageB = imgUtil.crop_bottom_notification(imageB)

    except:
        print(args["second"] + " Image file not found")
        return

    return imageA, imageB


def get_ssim(imageA, imageB):
    """convert the images to grayscale"""
    grayA = cv2.cvtColor(imageA, cv2.COLOR_BGR2GRAY)
    grayB = cv2.cvtColor(imageB, cv2.COLOR_BGR2GRAY)

    # compute the Structural Similarity Index (SSIM) between the two images
    (score, diff) = compare_ssim(grayA, grayB, full=True)
    return score


def print_result(val, text_mismatch):
    """SSIM val is in the range of -1 to 1. Similarity threshold we set is 0.8"""

    if val > 0.8 and text_mismatch <= 0.5:
        print("Test passed : Back button behavior as expected")
    else:
        print("Test failed : Back button behavior was unexpected ")
    global detailed_result
    if detailed_result:
        print(
            "===================================== DETAILED RESULT ====================================="
        )
        print("SSIM val is in the range of -1 to 1.The threshold for similarity is 0.8")
        print("Here the SSIM val is: {}".format(val))
        if text_mismatch != "":
            print("Text mismatch of {:.2%} ".format(text_mismatch))
        detailed_result = False


def findTrigger(app_name, listOfSteps, dim):
    """input: steps list from execution.json output: list of screen number where trigger clicked"""
    triggerList = {}
    # triggerIndex = []
    width = int(dim.split("x")[0])
    height = int(dim.split("x")[1])
    # print(width)
    for step in listOfSteps:
        if "dynGuiComponent" in step:
            dynGuiComponentData = step["dynGuiComponent"]
            command = step["textEntry"]
            try:
                # print(command, height)
                x = int(command.split(" ")[-2])
                y = int(command.split(" ")[-1])
            except Exception:
                continue

            if (
                dynGuiComponentData["idXml"] == "BACK_MODAL"
                or x < (width // 3)
                and (height - 200) <= y
                and "tap" in command
            ):
                # print(step["screenshot"])
                # triggerList.append(step["screenshot"])
                triggerList[str(step["sequenceStep"])] = step["screenshot"]
                # triggerIndex.append(step[""])
    return triggerList


def find_xml_from_screenshot(imagename, stepNum, args):
    xmlName = ""
    if tracePlayerGenerated:
        xmlName = imagename.split(".User-Trace")[0]
        xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"
    else:
        xmlName = imagename.split("screen")[0]
        xmlName += "ui-dump.xml"

    return os.path.join(args["bugId"], os.path.join("xmls", xmlName))


def get_image_names(args, imageName, image_num):

    """input: com.cohenadair.anglerslog.User-Trace.12.com.cohenadair.anglerslog_1441_AnglersLog19_augmented.png output: image name before back and after back clicked"""
    bugId = args["bugId"]
    appName = args["appName"]
    splitText = image_num + "_augmented"
    # splitText = bugId + "_" + appName
    # path = imageName.split("_augmented")[0]
    path = imageName.split(splitText)[0]

    # image_num = imageName.split(splitText)[1]
    # path = imageName.split(image_num)[0]
    index_f = int(image_num) - 2
    first_image_path = os.path.join(bugId, path) + str(index_f) + ".png"

    second_image_path = os.path.join(bugId, path) + str(image_num) + ".png"
    args["first"] = first_image_path
    args[first_image_path] = index_f
    args["second"] = second_image_path
    args[second_image_path] = image_num
    return


def get_image_before(args, key):
    # bugId = args["bugId"]
    # appName = args["appName"]
    image_name = args[key]
    index = args[image_name]
    splitText = str(index) + ".png"
    path = image_name.split(splitText)[0]
    before_image_path = path + str(int(index) - 1) + ".png"
    return before_image_path


def main():

    args = load_arguments()
    data = read_json(args["bugId"] + "/Execution-12.json")
    app_name = args["appName"]  # +"_"+args["bugid"]

    for line in data:
        if "deviceDimensions" in line:
            dim = data["deviceDimensions"]

        if "steps" in line:
            listOfSteps = data["steps"]
            print(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%    ORACLE FOR BACK BUTTON    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            )
            triggerScreens = findTrigger(app_name, listOfSteps, dim)
            # print(triggerScreens)
            print("Back was clicked {} time(s)".format(len(triggerScreens)))

    print(
        "-------------------------------------------------------------------------------------------"
    )
    # for i, trigger in enumerate(triggerScreens, 1):
    for i, trigger in triggerScreens.items():
        get_image_names(args, trigger, i)
        try:
            before_back, after_back = crop_image(args, trigger, i)
        except Exception:
            continue
        ssim_val = get_ssim(before_back, after_back)
        # print("Test result {} ".format(i))
        missing_frac = ""
        if ssim_val > 0.8:
            before_text = imgUtil.read_text_on_screen(
                args["bugId"],
                args["first"].split("/")[1],
            )
            after_text = imgUtil.read_text_on_screen(
                args["bugId"], args["second"].split("/")[1]
            )
            diff = set(before_text) - set(after_text)
            # print(len(diff), len(before_text), len(after_text))
            missing_frac = len(diff) / len(before_text)
        # print(missing_frac)

        # if missing_frac >= 0.5:
        # print("Text mismatch of {:.2%} ".format(missing_frac))
        # else:
        # print("Text matches")
        print_result(ssim_val, missing_frac)
        # print(args["first"])

        # print(after_text)

        # txt_from_before = sorted(xmlUtilities.readTextInXml(xmlPath))

        print(
            "-------------------------------------------------------------------------------------------"
        )


if __name__ == "__main__":
    main()
