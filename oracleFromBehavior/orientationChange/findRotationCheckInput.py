import json, os, sys
import xml.etree.ElementTree as ET
import argparse
from pprint import pprint

"""
This is the oracle for the screen orientation change. It finds the screen with trigger i.e. rotation=1.
 Reads the user inputs in the portrait screen before rotation
Edge cases handled:
1. Multiple trigger events.

Input: 19.xml, Execution-12.json (optional), readTextInImage.py, bugId, appName, need to add step in execution.json for landscape screen
Flags: detailed_result = display details of test oracle
       check_input_field = to compare text in user input fields
       check_all_text = to compare all text displayed in screen
"""

# Location of xmlUtilities.py
scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)
import xmlUtilities

# to display detailed result to developer
detailed_result = True
tracePlayerGenerated = False

# flags for what we want to check in oracle
check_input_field = True
check_all_text = True
check_all_images = True


def read_json(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def load_arguments():
    """construct the argument parse and parse the arguments"""

    ap = argparse.ArgumentParser()
    ap.add_argument("-a", "--appName", required=True, help="app name")
    ap.add_argument("-b", "--bugId", required=True, help="bug id")

    args = vars(ap.parse_args())
    return args


def find_xml_from_screenshot(imagename, stepNum, args):
    xmlName = ""
    if tracePlayerGenerated:
        xmlName = imagename.split(".User-Trace")[0]
        xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"
    else:
        xmlName = imagename.split("screen")[0]
        xmlName += "ui-dump.xml"
    return xmlName


def find_single_trigger(listOfSteps, args):
    """input: steps list from execution.json
    output: list of screen xml name as tuple of portrait and landscape screens"""
    """for cases where we want to detect landscape after portrait not vice versa"""
    triggerList = []
    landscape = 0
    lastPortrait = 0
    lastOrientation = ""
    for step in listOfSteps:
        stepNum = step["sequenceStep"]
        screenShotName = step["screenshot"]
        xmlName = find_xml_from_screenshot(screenShotName, stepNum, args)
        # print(screenShotName, xmlName)

        try:
            xmlPath = os.path.join(args["bugId"], os.path.join("xmls", xmlName))
            rotation = xmlUtilities.readXML(xmlPath).attrib["rotation"]
            # if rotation == "1":
            if rotation != lastOrientation and lastOrientation != "":
                landscape = xmlName  # screenShotName
                triggerList.append((lastPortrait, landscape))
            else:
                lastPortrait = xmlName  # screenShotName
        except:
            continue
    return triggerList


def find_trigger(listOfSteps, args):
    """input: steps list from execution.json
    output: list of screen xml name as tuple of portrait and landscape screens"""
    """detects landscape to portrait or portrait to landscape changes"""
    triggerList = []
    lastOrientationXML = 0
    currentOrientationXML = 0
    lastOrientation = ""

    for step in listOfSteps:
        stepNum = step["sequenceStep"]
        screenShotName = step["screenshot"]
        xmlName = find_xml_from_screenshot(screenShotName, stepNum, args)

        try:
            xmlPath = os.path.join(args["bugId"], os.path.join("xmls", xmlName))
            rotation = xmlUtilities.readXML(xmlPath).attrib["rotation"]
            if rotation != lastOrientation and lastOrientation != "":
                currentOrientationXML = xmlName
                triggerList.append((lastOrientationXML, currentOrientationXML))
                lastOrientation = rotation
            else:
                lastOrientationXML = xmlName
                lastOrientation = rotation
        except:
            continue
    return triggerList


def find_edit_text(screen, args):

    """input: portrait and landscape screenName list. output: map with screen number and USER ENTERED text"""

    screen_text_list = []
    holder = {}
    portrait, landscape = screen
    # print(screen)
    portraitXmlName = os.path.join(args["bugId"], os.path.join("xmls", portrait))
    landscapeXmlName = os.path.join(args["bugId"], os.path.join("xmls", landscape))

    # returns map of id and value
    holder["portrait"] = xmlUtilities.readUserFieldTextInXml(portraitXmlName)
    holder["landscape"] = xmlUtilities.readUserFieldTextInXml(landscapeXmlName)
    screen_text_list.append(holder)
    # print(screen_text_list)
    return screen_text_list


def find_all_images(screen, args):

    """input: portrait and landscape screenName list. output: map with screen number and ALL image resource_id"""

    images_list = []
    holder = {}
    portrait, landscape = screen
    portraitXmlName = os.path.join(args["bugId"], os.path.join("xmls", portrait))
    landscapeXmlName = os.path.join(args["bugId"], os.path.join("xmls", landscape))
    holder["portrait"] = xmlUtilities.return_resource_id_of_image(
        portraitXmlName
    )  # returns map of id and value
    holder["landscape"] = xmlUtilities.return_resource_id_of_image(landscapeXmlName)
    images_list.append(holder)

    return images_list


def find_all_text(screen, args):

    """input: portrait and landscape screenName list. output: map with screen number and ALL text"""

    screen_text_list = []
    holder = {}
    portrait, landscape = screen
    portraitXmlName = os.path.join(args["bugId"], os.path.join("xmls", portrait))
    landscapeXmlName = os.path.join(args["bugId"], os.path.join("xmls", landscape))
    holder["portrait"] = xmlUtilities.return_resource_id_with_text(
        portraitXmlName
    )  # returns map of id and value
    holder["landscape"] = xmlUtilities.return_resource_id_with_text(landscapeXmlName)
    screen_text_list.append(holder)
    # print(screen_text_list)
    return screen_text_list


def compare_text(userTextScreenMap, result):
    for screenPairs in userTextScreenMap:
        portrait_text_map = screenPairs["portrait"]
        landscape_text_map = screenPairs["landscape"]
        for id, text in portrait_text_map.items():
            if landscape_text_map.get(id) == text:
                result[text] = True
                entryFlag = True
            else:
                result[text] = False


def check_for_image(allImageScreenMap, result):
    for imageScreens in allImageScreenMap:
        portrait_image_list = imageScreens["portrait"]
        # print(portrait_image_list)
        landscape_image_list = imageScreens["landscape"]
        for id in portrait_image_list:
            if id in landscape_image_list:
                result[id] = True
                entryFlag = True
            else:
                result[id] = False
    # return result


def display_result(result_input_field, detailed_result, info, count, bad_frac):
    if result_input_field:
        missingText = [k for k, v in result_input_field.items() if not v]
        if bad_frac:  # and bad_frac > 0.5:
            if bad_frac > 0.5:
                print("Test failed: Text mismatch of {:.2%} ".format(bad_frac))
            else:
                print("Test passed : Most " + info + " shown")
        else:
            if missingText:
                print("Test failed : missing " + info)
            else:
                print("Test passed : All " + info + " shown")

        if detailed_result:
            print(
                "===================================== DETAILED RESULT ====================================="
            )
            print(info + " : is it on screen?")
            pprint(result_input_field)
    else:
        print("Test passed : No " + info + " in portrait to compare ")


def main():
    args = load_arguments()
    data = read_json(os.path.join(args["bugId"], "Execution-12.json"))
    textInScreenMap = {}
    result_input_field = {}
    result_all_text = {}
    result_all_image = {}
    triggerScreens = ""

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ORACLE FOR ORIENTATION CHANGE %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            )
            triggerScreens = find_trigger(listOfSteps, args)
            if triggerScreens:
                print("Orientation change detected")
            else:
                print("=== No orientation change detected ===")
            # triggerScreens.append('21') # Test case

            # print(triggerScreens)
    print(
        "-------------------------------------------------------------------------------------------"
    )

    for count, trigger in enumerate(triggerScreens):

        print(
            "==========================================================================================="
        )
        print(
            "-------------------------------------------------------------------------------------------"
        )
        print("Result for change", str(count + 1))

        userTextScreenMap = find_edit_text(trigger, args)

        allTextScreenMap = find_all_text(trigger, args)

        allImageScreenMap = find_all_images(trigger, args)

        # print(allTextScreenMap)

        test_count = 1
        if check_input_field:
            compare_text(userTextScreenMap, result_input_field)
            print(
                "------------------------------- Did user input(s) match? ----------------------------------"
            )

            display_result(
                result_input_field, detailed_result, "user input", str(test_count), ""
            )
            print(
                "-------------------------------------------------------------------------------------------"
            )
            test_count += 1

        if check_all_text:
            compare_text(allTextScreenMap, result_all_text)
            false_text = [1 for k, v in result_all_text.items() if not v]
            # print(len(false_text) / len(result_all_text))
            bad_frac = len(false_text) / len(result_all_text)

            print(
                "-------------------------------- Did text view(s) match? ----------------------------------"
            )
            display_result(
                result_all_text, detailed_result, "text view", str(test_count), bad_frac
            )
            print(
                "-------------------------------------------------------------------------------------------"
            )
            test_count += 1

        if check_all_images:
            check_for_image(allImageScreenMap, result_all_image)
            print(
                "------------------------------ Did image view(s) match? -----------------------------------"
            )
            display_result(
                result_all_image, detailed_result, "image(s)", str(test_count), ""
            )
            print(
                "-------------------------------------------------------------------------------------------"
            )
            test_count += 1


if __name__ == "__main__":
    main()
