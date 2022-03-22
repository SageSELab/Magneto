import json
import xmlUtilities
import xml.etree.ElementTree as ET

"""
This is the oracle for the screen orientation change. It finds the screen with trigger i.e. rotation=1.
 Reads the user inputs in the portrait screen before rotation
Edge cases handled:
1. Multiple trigger events.

Input: 19.xml, Execution-12.json, readTextInImage.py, bugId, appName, need to add step in execution.json for landscape screen
Flags: detailed_result = display details of test oracle
       check_input_field = to compare text in user input fields
       check_all_text = to compare all text displayed in screen
"""

appName = "anki"
bugId = "273"
detailed_result = True
check_input_field = True
check_all_text = True
check_all_images = True


def readJson(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def find_trigger(listOfSteps):
    """input: steps list from execution.json
    output: list of screen xml name as tuple of portrait and landscape screens"""
    triggerList = []
    landscape = 0
    lastPortrait = 0
    for step in listOfSteps:
        stepNum = step["sequenceStep"]
        screenShotName = step["screenshot"]
        screenShotName = (
            screenShotName.split(".User-Trace")[0]
            + "-"
            + bugId
            + "-12-User-Trace-"
            + str(stepNum)
            + ".xml"
        )
        # print(screenShotName)

        try:
            rotation = xmlUtilities.readXML("xmls/" + screenShotName).attrib["rotation"]
            if rotation == "1":
                landscape = screenShotName
                triggerList.append((lastPortrait, landscape))
            else:
                lastPortrait = screenShotName
        except:
            continue
    return triggerList


def find_edit_text(triggerScreens):

    """input: portrait and landscape screenName list. output: map with screen number and USER ENTERED text"""

    screen_text_list = []
    for screen in triggerScreens:
        holder = {}
        portrait, landscape = screen
        holder["portrait"] = xmlUtilities.readUserFieldTextInXml(
            "xmls/" + portrait
        )  # returns map of id and value
        holder["landscape"] = xmlUtilities.readUserFieldTextInXml("xmls/" + landscape)
        screen_text_list.append(holder)

    return screen_text_list


def find_all_images(triggerScreens):

    """input: portrait and landscape screenName list. output: map with screen number and ALL image resource_id"""

    images_list = []
    for screen in triggerScreens:
        holder = {}
        portrait, landscape = screen
        holder["portrait"] = xmlUtilities.return_resource_id_of_image(
            "xmls/" + portrait
        )  # returns map of id and value
        holder["landscape"] = xmlUtilities.return_resource_id_of_image(
            "xmls/" + landscape
        )
        images_list.append(holder)

    return images_list


def find_all_text(triggerScreens):

    """input: portrait and landscape screenName list. output: map with screen number and ALL text"""

    screen_text_list = []
    for screen in triggerScreens:
        holder = {}
        portrait, landscape = screen
        holder["portrait"] = xmlUtilities.return_resource_id_with_text(
            "xmls/" + portrait
        )  # returns map of id and value
        holder["landscape"] = xmlUtilities.return_resource_id_with_text(
            "xmls/" + landscape
        )
        screen_text_list.append(holder)
    print(screen_text_list)
    return screen_text_list


# def processImageName(imageName):
#
#     ''' input: com.cohenadair.anglerslog.User-Trace.12.com.cohenadair.anglerslog_1441_AnglersLog19_augmented.png output: 19'''
#
#     imageName=imageName.split(appName)[1].split("_augmented")[0];
#     return imageName

# def readTextInScreenAfterTrigger(screen, textInScreenMap):
#
#     ''' input: screen number after trigger clicked
#         output: map with screen number and list of text in screen '''
#
#     textList = readTextInXml(str(screen)+".xml")
#     textInScreenMap[screen] = textList
#
#     return textInScreenMap


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
        print(portrait_image_list)
        landscape_image_list = imageScreens["landscape"]
        for id in portrait_image_list:
            if id in landscape_image_list:
                result[id] = True
                entryFlag = True
            else:
                result[id] = False
    # return result


def display_result(result_input_field, detailed_result, info, count):
    missingText = [k for k, v in result_input_field.items() if not v]
    if missingText:
        print(
            "================== Test "
            + count
            + " failed : missing "
            + info
            + " ==================="
        )
    else:
        print(
            "================== Test "
            + count
            + " passed : All "
            + info
            + " shown ==================="
        )

    if detailed_result:
        print("==================DETAILED RESULT===================")
        print(info + " : is it on screen?")
        print(result_input_field)


def main():

    data = readJson("Execution-12.json")
    textInScreenMap = {}
    result_input_field = {}
    result_all_text = {}
    result_all_image = {}

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print("Look for triggers-------------------")
            triggerScreens = find_trigger(listOfSteps)
            print(triggerScreens, "===")
            # triggerScreens.append('21') # Test case
            print(
                "Look for user entered data before and after screen rotation------------------"
            )
            userTextScreenMap = find_edit_text(triggerScreens)
            allTextScreenMap = find_all_text(triggerScreens)
            allImageScreenMap = find_all_images(triggerScreens)

            # print(allTextScreenMap)

    test_count = 1
    if check_input_field:
        compare_text(userTextScreenMap, result_input_field)
        display_result(
            result_input_field, detailed_result, "user input", str(test_count)
        )
        test_count += 1

    if check_all_text:
        compare_text(allTextScreenMap, result_all_text)
        display_result(result_all_text, detailed_result, "text", str(test_count))
        test_count += 1

    if check_all_images:
        check_for_image(allImageScreenMap, result_all_image)
        display_result(result_all_image, detailed_result, "image", str(test_count))
        test_count += 1

    # check_input_field(userTextScreenMap,result_all_text)
    #
    # missingText = [k for k,v in result_all_text.items() if not v]
    # if(missingText):
    #     print("================== Test failed : missing user input ===================")
    # else:
    #     print("================== Test passed : All user input shown ===================")
    #
    # if(detailed_result):
    #     print("==================DETAILED RESULT===================")
    #     print("User input : is it on screen?")
    #     print(result_all_text)


if __name__ == "__main__":
    main()
