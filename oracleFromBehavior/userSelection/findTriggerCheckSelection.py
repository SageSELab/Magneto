import json, sys, os

# from readTextInImage import readTextInXml

scriptLocation = os.getcwd()
dirName = os.path.dirname(scriptLocation)
sys.path.insert(1, dirName)
import readTextInImage

"""
CURRENTLY ADDED TO findTriggerCheckInput.py
This is the oracle for this user made selection. It finds the screen with trigger words.
 Reads the user selection in the trigger screen and compares the user selection with the word in the screen after trigger event
pressed.
Edge cases handled:
1. Multiple trigger events.
2. User input displayed in a list or substring of larger string.

Input: 19.xml, Execution-12.json, readTextInImage.py, appName
"""

appName = sys.argv[1]  # "142_QKSMS"  # "GnuCash-1222"
bugId = sys.argv[2]

detailedResult = True


def readJson(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def findTriggerAndSelections(listOfSteps, listOfTriggerWords, listOfUserEnteredField):
    """input: steps list from execution.jsonm list of trigger words, list of user entered fields
    output: tuple of trigger screens, text and screen map of trigger screens, map of image name and count"""
    triggerList = []  # list of screens with triggers
    screenTextMap = {}  # screen and text mappings
    screen_count_map = {}  # to keep track of long image names and simple counters
    for step in listOfSteps:
        if "dynGuiComponent" in step:
            dynGuiComponentData = step["dynGuiComponent"]
            buttonText = dynGuiComponentData["text"].lower()
            if dynGuiComponentData["name"] == "android.widget.Button" and any(
                words in buttonText for words in listOfTriggerWords
            ):
                # imagebutton that has 'done', 'save', .. in name
                imageNumber, imageName = processImageName(step["screenshot"])
                screen_count_map[imageName] = imageNumber
                triggerList.append(imageName)
                if "screen" in step:
                    dynGuiComponentDataOfScreen = step["screen"]["dynGuiComponents"]
                    for element in dynGuiComponentDataOfScreen:
                        if (
                            element["name"] in listOfUserEnteredField
                            and True == element["checked"]
                        ):
                            if imageNumber in screenTextMap:
                                newTmpList = screenTextMap[imageNumber]
                                newTmpList.append(element["text"])
                                screenTextMap[imageNumber] = newTmpList
                            else:
                                screenTextMap[imageNumber] = [element["text"]]

    return triggerList, screenTextMap, screen_count_map


def processImageName(imageName):

    """input: com.cohenadair.anglerslog.User-Trace.12.com.cohenadair.anglerslog_1441_AnglersLog19_augmented.png
    output: com.cohenadair.anglerslog-1441-12-User-Trace-18.xml"""

    num = imageName.split(appName)[1].split("_augmented")[0]
    imageName = imageName.split(".User-Trace")[0]
    imageName = imageName + "-" + bugId + "-12-User-Trace-" + num + ".xml"
    return num, imageName


def readTextInScreenAfterTrigger(screen):

    """input: screen number after trigger clicked
    output: map with screen number and list of text in screen"""

    textInScreenMap = {}
    screenName = os.path.join(bugId, screen)
    textList = readTextInImage.readTextInXml(screenName)
    textInScreenMap[screen] = textList

    return textInScreenMap


def createTriggerList():
    listOfTriggerWords = []
    listOfTriggerWords.append("done")
    listOfTriggerWords.append("set")
    listOfTriggerWords.append("ok")
    listOfTriggerWords.append("save")
    # listOfTriggerWords.append("export") # "name": "android.widget.TextView" not button

    return listOfTriggerWords


def createComponentSearchList():
    listOfComponents = []
    listOfComponents.append("android.widget.CheckedTextView")
    # listOfComponents.append("android.widget.EditText")
    listOfComponents.append("android.widget.ToggleButton")
    return listOfComponents


def main():
    data = readJson(os.path.join(bugId, "Execution-12.json"))
    listOfTriggerWords = createTriggerList()
    listOfUserEnteredField = createComponentSearchList()
    textInScreenMap = {}
    result = {}
    # userTextScreenMap = {}
    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print("Look for triggers and user entered data-------------------")
            (
                triggerScreenList,
                userTextScreenMap,
                screen_count_map,
            ) = findTriggerAndSelections(
                listOfSteps, listOfTriggerWords, listOfUserEnteredField
            )

    firstTriggerScreen = 0

    for trigger in triggerScreenList:
        print("Read text on screen after trigger------------------")
        triggerScreenCounter = screen_count_map.get(trigger)

        textInScreenMap = readTextInScreenAfterTrigger(trigger)

        relevantUserInput = userTextScreenMap.get(
            triggerScreenCounter
        )  # the trigger screen is where we look for final user selections
        if relevantUserInput:
            for input in relevantUserInput:
                entryFlag = False
                splitted = False
                entryList = []
                for entry in textInScreenMap[trigger]:
                    if "," or " " in entry:
                        if "," and " " in entry:
                            entryList = entry.split(", ")
                            for e in entryList:
                                if " " in e:
                                    entryList.remove(e)
                                    entryList = entryList + e.split(" ")
                        elif "," in entry:
                            entryList = entry.split(", ")
                        elif " " in entry:
                            entryList = entry.split(" ")

                        for e in entryList:
                            if input == e:
                                result[input] = True
                                entryFlag = True
                                break
                    else:
                        if input == entry:
                            result[input] = True
                            entryFlag = True
                if not entryFlag:
                    result[input] = False

        firstTriggerScreen = triggerScreenCounter

    missingText = [k for k, v in result.items() if not v]
    if missingText:
        print(
            "================== Test failed : missing user selection ==================="
        )
    else:
        print(
            "================== Test passed : All user selection shown ==================="
        )

    if detailedResult:
        print("==================DETAILED RESULT===================")
        print("User selection : is it on screen?")
        print(result)


if __name__ == "__main__":
    main()
