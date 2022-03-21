from email.mime import image
from posixpath import split
import cv2
import numpy as np
import argparse
import colour  # for delta_E calc :  pip3 install colour-science

import json, os, sys
import difflib

scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)
import imageUtilities as imgUtil
import xmlUtilities
import labelPredictor


detailedResult = True
tracePlayerGenerated = True


def load_arguments():
    """construct the argument parse and parse the arguments"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--appName", required=True, help="appName")
    ap.add_argument("-b", "--bugId", required=True, help="bug id")

    args = vars(ap.parse_args())
    return args


def read_json(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def create_trigger_list():
    listOfTriggerWords = []
    listOfTriggerWords.append("theme")
    listOfTriggerWords.append("night")

    return listOfTriggerWords


def create_component_list():
    """List of components potentially used for theme change"""
    listOfComponents = []
    listOfComponents.append("switch")
    listOfComponents.append("radio")
    listOfComponents.append("checkbox")
    listOfComponents.append("toggle")

    return listOfComponents


def check_if_theme_set(
    image_name, xmlPath, tapPos, tappedComponent, listOfTriggerWords
):
    """checks if the interacted component was theme or if it was switch, toggle beside the word theme"""
    """returns two boolean for theme Changed? , one step theme changed?"""
    try:
        tapY = tapPos[-1] if tapPos else "-1"
        tapX = tapPos[-2] if len(tapPos) > 1 else "-1"
        # print(image_name)
        # in case no tap info
        if tapX == "-1" or tapY == "-1":
            return False, False
        text = imgUtil.readTextInImage(image_name)
        listOfComponents = create_component_list()
        if "theme" in text.lower():
            # print(xmlPath, "THEME SET", image_name)
            return True, False
        else:
            startY, endY = xmlUtilities.findParentBoundOfMatchingNode(
                xmlPath, listOfTriggerWords
            )

            # check if clicked component is at same height as the word "theme"
            if int(startY) < int(tapY) < int(endY):
                if any(words in tappedComponent.lower() for words in listOfComponents):
                    return True, True

        return False, False

    except Exception as e:
        # catches error from findParentBoundOfMatchingNode
        # print(e.__class__)
        # print(e.__cause__)
        return False, False


def find_xml_from_screenshot(imagename, stepNum, args):
    xmlName = ""
    if tracePlayerGenerated:
        xmlName = imagename.split(".User-Trace")[0]
        xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"
    else:
        xmlName = imagename.split("screen")[0]
        xmlName += "ui-dump.xml"

    return os.path.join(args["bugId"], os.path.join("xmls", xmlName))


def get_step_details(step):

    screen_index = step["sequenceStep"]
    tapPosition = step["textEntry"].split(" ")
    if "dynGuiComponent" in step:
        clicked_comp_name = step["dynGuiComponent"]["name"]
    else:
        clicked_comp_name = ""

    return screen_index, tapPosition, clicked_comp_name


def find_trigger_reading_image(listOfSteps, screen_count_map, listOfTriggerWords, args):
    """input: steps list from execution.json
    output: list of screen number where trigger clicked"""
    screen_background = "light"
    triggerList = []
    theme_set = False
    correct_screen_found = False
    correct_theme_index = None
    text_in_trigger_screen = ""
    correct_screen = None
    correct_affected_image_map = {}
    image_xml_map = {}
    bugId = args["bugId"]
    correct_xml = None
    themeChangeSuccess = {}
    before_theme = ""
    # themeChanged = False
    oneStep = False
    # nextScreen = False
    lastScreen = ""
    for step in listOfSteps:

        if theme_set:
            oneStep = True

        start_screen = step["screenshot"]
        clicked_screen = start_screen.replace("augmented", "gui")
        result_screen = start_screen.replace("_augmented", "")

        screen_index, tapPos, clicked_comp_name = get_step_details(step)

        clicked_Image = os.path.join(bugId, clicked_screen)
        xmlPath = find_xml_from_screenshot(start_screen, screen_index, args)

        image_xml_map[result_screen] = xmlPath

        if theme_set and correct_screen_found and screen_index > correct_theme_index:
            correct_affected_image_map[correct_screen].append(result_screen)

        if not theme_set:
            themeChanged, oneStep = check_if_theme_set(
                clicked_Image, xmlPath, tapPos, clicked_comp_name, listOfTriggerWords
            )
        if themeChanged and not theme_set:
            # print("YUP", xmlPath)
            if not oneStep:
                xmlPath = find_xml_from_screenshot(lastScreen, screen_index - 1, args)
            text_in_trigger_screen = sorted(xmlUtilities.readTextInXml(xmlPath))
            # print(xmlPath)
            # print(text_in_trigger_screen)
            theme_set = True
            correct_screen_found = False
            before_theme = imgUtil.is_image_light(os.path.join(bugId, start_screen))
        lastScreen = start_screen
        if theme_set and not correct_screen_found and oneStep:
            # print("HEREHERE")
            text_in_screen = sorted(xmlUtilities.readTextInXml(xmlPath))
            # this detects the screen before theme change completed, assume the theme here is correct
            seq_mat = difflib.SequenceMatcher()
            seq_mat.set_seqs(text_in_screen, text_in_trigger_screen)
            match_ratio = seq_mat.ratio()
            # print(match_ratio, xmlPath)
            # print(text_in_screen)
            if match_ratio >= 0.90:
                correct_screen_found = True
                correct_screen = result_screen
                correct_xml = xmlPath
                correct_theme_index = screen_index
                triggerList.append(correct_screen)
                correct_affected_image_map[correct_screen] = []
                after_theme = imgUtil.is_image_light(os.path.join(bugId, result_screen))
                if before_theme != after_theme:
                    themeChangeSuccess[correct_screen] = True
                else:
                    themeChangeSuccess[correct_screen] = False
                # continue
        # print(triggerList, correct_affected_image_map)

    return triggerList, correct_affected_image_map, image_xml_map, themeChangeSuccess

def check_if_keyboard_visible(imageName):
    img = cv2.imread(imageName)
    croppedA = imgUtil.crop_keyboard(img)
    return labelPredictor.has_keyboard(croppedA)

def main():

    args = load_arguments()
    bugId = args["bugId"]
    screen_count_map = {}

    data = read_json(os.path.join(bugId, "Execution-12.json"))
    listOfTriggerWords = create_trigger_list()

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%  ORACLE FOR THEME CHANGE  %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            )
            (
                triggerList,
                correct_affected_image_map,
                image_xml_map,
                themeChangeSuccess,
            ) = find_trigger_reading_image(
                listOfSteps, screen_count_map, listOfTriggerWords, args
            )

    if len(triggerList) >= 1:
        print("Theme change detected")

        # if not themeChangeSuccess:
        #     print("Theme change was not successful")
        # else:
        #     print("Theme changed successfully")
    else:
        print("Theme change not detected")
        return

    print(
        "--------------------------- Was theme changed successfully? -------------------------------"
    )
    # check if theme changed successfully
    for trigger in triggerList:
        if themeChangeSuccess[trigger]:
            print("Theme changed successfully")
        else:
            print("Theme change was not successful")
            return

    print(
        "---------------------------- Did theme match in all screen? -------------------------------"
    )
    # check if theme of all screen match
    for trigger in triggerList:
        all_affected_images = correct_affected_image_map[trigger]
        hasKeyboard = check_if_keyboard_visible(os.path.join(bugId, trigger))
        print(trigger, bugId)
        lab1 = imgUtil.get_lab_val(os.path.join(bugId, trigger), hasKeyboard, None)
        for affected_image in all_affected_images:
            hasKeyboard = check_if_keyboard_visible(os.path.join(bugId, affected_image))
            xmlPath = image_xml_map[affected_image]
            bounds = getFocusedElement(xmlPath)

            lab2 = imgUtil.get_lab_val(os.path.join(bugId, affected_image), hasKeyboard, bounds)
            is_theme_matching(lab1, lab2, trigger, affected_image)

    print(
        "---------------------------- Did all text show in dark theme? ------------------------------"
    )
    # check if text is seen in all screen after theme change. Compare ocr result with text in xml
    for trigger in triggerList:
        all_affected_images = correct_affected_image_map[trigger]
        for affected_image in all_affected_images:
            xmlPath = image_xml_map[affected_image]
            is_text_displayed(bugId, affected_image, xmlPath)


def preprocess_text(txt):
    result = []
    for t in txt:
        t = t.replace("\n", " ").lower().strip()
        t = t.replace("  ", " ")
        result.append(t)

    return result

def getFocusedElement(xmlPath):
    bounds = xmlUtilities.readBoundOfFocusedElement(xmlPath)
    return bounds
    # print(bounds)


def is_text_displayed(bugId, affected_image, xmlPath):
    txt_from_img = sorted(imgUtil.read_text_on_screen(bugId, affected_image))
    txt_from_xml = sorted(xmlUtilities.readTextInXml(xmlPath))
    seq_mat = difflib.SequenceMatcher()
    # print(preprocess_text(txt_from_img))
    txt_from_img = preprocess_text(txt_from_img)
    txt_from_xml = preprocess_text(txt_from_xml)

    diff = set(txt_from_xml) - set(txt_from_img)
    bad_frac = len(diff) / len(txt_from_xml)
    # print(diff)
    # print(affected_image)
    # seq_mat.set_seqs(txt_from_img, txt_from_xml)
    # print(txt_from_img)
    # print(txt_from_xml)
    # print(txt_from_xml)
    # print(txt_from_img)
    # match_ratio = seq_mat.ratio()
    # if match_ratio >= 0.50:
    if bad_frac <= 0.5:
        print("Most text shows in ", affected_image)
    else:
        print("{:.2%} of text didn't show in".format(bad_frac), affected_image)
        # print("Text didn't show in ", affected_image, bad_ratio, "%")


def is_theme_matching(lab1, lab2, trigger, affected_image):
    delta_E = colour.delta_E(lab1, lab2)

    # A result less than 2 is generally considered to be perceptually equivalent.
    if delta_E > 2:
        print(
            "Test failed : the theme change is inconsistent on image",
            affected_image,
        )
    else:
        print("Test passed : the theme is consistent on image", affected_image)
    global detailedResult
    if detailedResult:
        print(
            "===================================== DETAILED RESULT ====================================="
        )

        print(
            "If delta_E value of two images is less than 2, the images are generally considered to be perceptually equivalent."
        )
        print(
            "The delta_E value for this images compared to ",
            trigger,
            " is ",
            delta_E,
        )
        showContext = False
        print(
            "-------------------------------------------------------------------------------------------"
        )


if __name__ == "__main__":
    main()
