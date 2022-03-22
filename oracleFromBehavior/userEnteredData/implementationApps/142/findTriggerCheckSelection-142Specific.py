import json, sys, os

# from readTextInImage import readTextInXml

sys.path.insert(1, "/Users/kesina/Documents/BugReportOracle/")
import readTextInImage


"""
This is the oracle for this user made selection. It finds the screen with trigger words.
 Reads the user selection in the trigger screen and compares the user selection with the word in the screen after trigger event
pressed.
Edge cases handled:
1. Multiple trigger events.
2. User input displayed in a list or substring of larger string.

Input: 19.xml, Execution-12.json, readTextInImage.py, appName
"""

appName = "142_QKSMS"
detailedResult = True


def readJson(jsonName):
    with open(jsonName) as f:
        data = json.load(f)
    return data


def findTrigger(listOfSteps, listOfTriggerWords):
    """input: steps list from execution.json and list of trigger words
    output: list of sequence steps where trigger clicked"""
    triggerList = []
    for step in listOfSteps:
        if "dynGuiComponent" in step:
            dynGuiComponentData = step["dynGuiComponent"]
            buttonText = dynGuiComponentData["text"].lower()
            # if (dynGuiComponentData['name'] == 'android.widget.ImageButton' and 'done' in dynGuiComponentData['idXml']) or
            if dynGuiComponentData["name"] == "android.widget.Button" and any(
                words in buttonText for words in listOfTriggerWords
            ):
                # imagebutton that has 'done', 'save', .. in name
                triggerList.append(step)
    return triggerList


def findUserSelection(triggerScreenList, listOfUserEnteredField):
    """input: trigger steps list from execution.json output: map with screen number and user selected data"""

    screenTextMap = {}

    for step in triggerScreenList:
        if "screen" in step:
            dynGuiComponentDataOfScreen = step["screen"]["dynGuiComponents"]
            for element in dynGuiComponentDataOfScreen:
                if (
                    element["name"] == "android.widget.EditText"
                    and "none" in step["textEntry"]
                ) or (
                    element["name"] == "android.widget.CheckedTextView"
                    and True == element["checked"]
                ):  # edit field and didn't send tap event
                    imageNumber = processImageName(step["screenshot"])
                    screenTextMap[imageNumber] = element["text"]
    return screenTextMap


def processImageName(imageName):

    """input: com.cohenadair.anglerslog.User-Trace.12.com.cohenadair.anglerslog_1441_AnglersLog19_augmented.png output: 19"""
    imageName = imageName.split(appName)[1].split("_augmented")[0]

    return imageName


def readTextInScreenAfterTrigger(screen, textInScreenMap):

    """input: screen number after trigger clicked
    output: map with screen number and list of text in screen"""

    textList = readTextInImage.readTextInXml(screen + ".xml")
    textInScreenMap[screen] = textList

    return textInScreenMap


def createTriggerList():
    listOfTriggerWords = []
    listOfTriggerWords.append("done")
    listOfTriggerWords.append("set")
    listOfTriggerWords.append("ok")
    listOfTriggerWords.append("save")
    return listOfTriggerWords


def createComponentSearchList():
    listOfComponents = []
    listOfComponents.append("android.widget.CheckedTextView")
    listOfComponents.append("android.widget.EditText")
    return listOfComponents


def main():
    data = readJson("Execution-12.json")
    listOfTriggerWords = createTriggerList()
    listOfUserEnteredField = createComponentSearchList()
    textInScreenMap = {}
    result = {}
    userTextScreenMap = {}
    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print("Look for triggers-------------------")
            triggerScreenList = findTrigger(listOfSteps, listOfTriggerWords)
            print("Look for user entered data------------------")
            userTextScreenMap = findUserSelection(
                triggerScreenList, listOfUserEnteredField
            )
    firstTriggerScreen = 0

    for trigger in triggerScreenList:
        print("Read text on screen after trigger------------------")
        screenNumber = processImageName(trigger["screenshot"])
        textInScreenMap = readTextInScreenAfterTrigger(screenNumber, textInScreenMap)

        for screen, text in userTextScreenMap.items():
            if int(screenNumber) == int(
                screen
            ):  # the trigger screen is where we look for final user selections
                entryFlag = False
                for entry in textInScreenMap[screenNumber]:
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

        firstTriggerScreen = screenNumber

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
