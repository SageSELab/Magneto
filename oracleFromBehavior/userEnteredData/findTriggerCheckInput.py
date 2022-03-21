import json
import sys, os
from pprint import pprint
import argparse


"""
This is the oracle for this user entered text. It finds the screen with trigger words.
 Reads all the user inputs until the trigger event and checks for the user input in the screen after trigger event
pressed.
Edge cases handled:
1. Multiple trigger events.
2. User input displayed in a list or substring of larger string.

Input: 19.xml, Execution-12.json, readTextInImage.py
"""

# Location of xmlUtilities.py
scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)
import xmlUtilities

detailedResult = True
tracePlayerGenerated = True


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


def find_trigger(
    listOfSteps, screen_count_map, listOfTriggerWords, listOfTriggerComponents, args
):
    """input: steps list from execution.json
    output: list of screen number where trigger clicked"""
    triggerList = []
    for step in listOfSteps:
        if "dynGuiComponent" in step:
            dynGuiComponentData = step["dynGuiComponent"]
            buttonText = dynGuiComponentData["idXml"].lower()
            buttonName = dynGuiComponentData["name"]
            if any(comp == buttonName for comp in listOfTriggerComponents) and any(
                words in buttonText for words in listOfTriggerWords
            ):
                # "done" in dynGuiComponentData["idXml"]
                # ):  # imagebutton that has done or save in name
                # print(step['screenshot'])
                # imageNumber, imageName = process_image_name(step["screenshot"], args)
                # print(buttonText, "===", buttonName)
                imageNumber = step["sequenceStep"]
                # imageNumber, xmlPath = process_image_name(step["screenshot"], args)
                imagePath, imageName = find_xml_from_screenshot(
                    step["screenshot"], imageNumber, args
                )
                screen_count_map[imageName] = imageNumber
                triggerList.append(imageName)
    return triggerList


def find_xml_from_screenshot(imagename, stepNum, args):
    xmlName = ""
    if tracePlayerGenerated:
        xmlName = imagename.split(".User-Trace")[0]
        xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"
    else:
        xmlName = imagename.split("screen")[0]
        xmlName += "ui-dump.xml"

    return os.path.join(args["bugId"], os.path.join("xmls", xmlName)), xmlName


def find_edit_text(listOfSteps, screen_count_map, args):

    """input: steps list from execution.json output: map with screen number and user entered text"""

    screenTextMap = {}
    screen_count_name_map = {}
    for step in listOfSteps:
        if "dynGuiComponent" in step:
            dynGuiComponentData = step["dynGuiComponent"]
            if (
                dynGuiComponentData["name"] == "android.widget.EditText"
                and "none" in step["textEntry"]
            ):
                # edit field and didn't send tap event because text input entered
                imageNumber = step["sequenceStep"]
                # imageNumber, xmlPath = process_image_name(step["screenshot"], args)
                xmlPath = find_xml_from_screenshot(
                    step["screenshot"], imageNumber, args
                )
                screen_count_name_map[xmlPath] = imageNumber
                screenTextMap[imageNumber] = dynGuiComponentData["text"]
    return screenTextMap


def process_image_name(imageName, args):

    """input: com.cohenadair.anglerslog.User-Trace.12.com.cohenadair.anglerslog_1441_AnglersLog19_augmented.png
    output: com.cohenadair.anglerslog-1441-12-User-Trace-18.xml"""

    num = imageName.split(args["appName"])[1].split("_augmented")[0]
    # return imageName
    imageName = imageName.split(".User-Trace")[0]
    imageName = imageName + "-" + args["bugId"] + "-12-User-Trace-" + num + ".xml"
    return num, imageName


def read_text_in_screen_after_trigger(screen, textInScreenMap, args):

    """input: screen number after trigger clicked
    output: map with screen number and list of text in screen"""
    screenName = os.path.join(args["bugId"], screen)
    # after save or set, input appears as textView
    textList = xmlUtilities.readTextInXml(screenName)
    textInScreenMap[screen] = textList

    # return textInScreenMap


def create_trigger_component_list():
    listOfTriggerComponents = []
    listOfTriggerComponents.append("android.widget.Button")
    listOfTriggerComponents.append("android.widget.ImageButton")
    listOfTriggerComponents.append("android.widget.TextView")

    return listOfTriggerComponents


def create_trigger_word_list():
    listOfTriggerWords = []
    listOfTriggerWords.append("done")
    listOfTriggerWords.append("set")
    listOfTriggerWords.append("ok")
    listOfTriggerWords.append("save")
    listOfTriggerWords.append("add")
    # listOfTriggerWords.append("export") # "name": "android.widget.TextView" not button

    return listOfTriggerWords


def main():
    args = load_arguments()
    data = read_json(os.path.join(args["bugId"], "Execution-12.json"))

    listOfTriggerWords = create_trigger_word_list()
    listOfTriggerComponents = create_trigger_component_list()
    textInScreenMap = {}
    screen_count_map = {}
    result = {}

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print(
                "%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% ORACLE FOR USER INPUT MATCH %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%"
            )
            triggerScreens = find_trigger(
                listOfSteps,
                screen_count_map,
                listOfTriggerWords,
                listOfTriggerComponents,
                args,
            )
            if triggerScreens:
                print("User input detected")
            else:
                print("=== No user input detected ===")
            # triggerScreens.append('21') # Test case

            # all edit text content as screen index, text map
            usertext_screen_map = find_edit_text(listOfSteps, screen_count_map, args)
            # usertext_screen_map['20'] = 'sth'  # Test case
            # usertext_screen_map['18'] ='37.421998' # Test case
    first_trigger_screen = 0
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
        read_text_in_screen_after_trigger(trigger, textInScreenMap, args)

        trigger_screen_index = screen_count_map.get(trigger)  # screen index map

        # compare text for every screen between one trigger or start to next trigger
        result = compareText(
            usertext_screen_map,
            textInScreenMap,
            trigger,
            trigger_screen_index,
            first_trigger_screen,
        )

        # keep track of last trigger screen if multiple
        first_trigger_screen = trigger_screen_index

        display_result(result)
        print(
            "-------------------------------------------------------------------------------------------"
        )


def display_result(result):
    if not result:
        print("Test passed: no user input set")
    else:
        missingText = [k for k, v in result.items() if not v]
        if missingText:
            print("Test failed : missing user input")
        else:
            print("Test passed : all user input shown")

        if detailedResult:
            print(
                "===================================== DETAILED RESULT ====================================="
            )
            print("User input : is it on screen?")
            pprint(result)

        print(
            "-------------------------------------------------------------------------------------------"
        )


def compareText(
    usertext_screen_map,
    textInScreenMap,
    trigger,
    trigger_screen_index,
    first_trigger_screen,
):

    result = {}
    # compare text for every screen between one trigger or start to next trigger
    for current_screen_index, text in usertext_screen_map.items():
        if int(first_trigger_screen) < int(current_screen_index) and int(
            current_screen_index
        ) < int(trigger_screen_index):
            entryFlag = False
            for entry in textInScreenMap[trigger]:
                if "," in entry or " " in entry:
                    if "," in entry:
                        entry = entry.split(", ")
                    elif " " in entry:
                        entry = entry.split(" ")
                    for e in entry:
                        if text == e:
                            result[text] = True
                            entryFlag = True
                else:
                    if text == entry:
                        result[text] = True
                        entryFlag = True
            if not entryFlag:
                result[text] = False

    return result


if __name__ == "__main__":
    main()
