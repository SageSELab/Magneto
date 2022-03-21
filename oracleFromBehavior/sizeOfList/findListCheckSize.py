import json, os, sys

import xml.etree.ElementTree as ET
import argparse

"""
This is the oracle for the checking list row size. It finds the screen with trigger i.e. containing recycler view.
 Finds the size of row container, text container and checks if the height is consistent 


Input: 19.xml, Execution-12.json, readTextInImage.py, bugId, appName, need to add step in execution.json for landscape screen
Flags: detailed_result = display details of test oracle
       
"""

sys.path.insert(1, "/Users/kesina/Documents/BugReportOracle/")
import xmlUtilities

detailed_result = True


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


def find_xml_from_screenshot(imagename, stepNum, args):
    xmlName = imagename.split(".User-Trace")[0]
    xmlName += "-" + args["bugId"] + "-12-User-Trace-" + str(stepNum) + ".xml"
    return xmlName


def find_trigger(listOfSteps, args):
    """input: steps list from execution.json
    output: list of screen xml name as tuple of portrait and landscape screens"""
    xml_with_off_rows = []
    rows_xml_map = {}
    for step in listOfSteps:
        stepNum = step["sequenceStep"]
        screenShotName = step["screenshot"]
        xmlName = find_xml_from_screenshot(screenShotName, stepNum, args)
        # print(xmlName, "-------------")

        try:
            list_of_recycle_classes = get_list_of_recycle_classes()
            list_of_container_classes = get_list_of_container_classes()

            xmlPath = os.path.join(args["bugId"], os.path.join("xmls", xmlName))
            # xml_with_off_rows = xmlUtilities.find_recycler_class(
            #     xmlPath, list_of_recycle_classes, list_of_container_classes
            # )
            rows = xmlUtilities.find_recycler_class_only(
                xmlPath, list_of_recycle_classes
            )
            rows_xml_map[xmlName] = rows
        except Exception:
            continue
    # return xml_with_off_rows
    return rows_xml_map


def get_list_of_container_classes():
    result = []
    result.append("android.widget.LinearLayout")
    return result


def get_list_of_recycle_classes():
    result = []
    result.append("android.support.v7.widget.RecyclerView")
    result.append("androidx.recyclerview.widget.RecyclerView")
    return result


def check_container_text_size(rows_xml_map):
    bad_xml_map = {}
    list_of_container_classes = get_list_of_container_classes()
    for xmlName, childrens in rows_xml_map.items():
        for children in childrens:
            for child in children:
                if child.getAttribute("class") in list_of_container_classes:
                    # found the container
                    container_bound = child.getAttribute("bounds")
                    container_start_height = int(
                        container_bound.split("][")[0].split(",")[1]
                    )
                    list_row = child.getElementsByTagName("node")
                    for i in list_row:
                        row_bound = i.getAttribute("bounds")
                        row_start_height = int(row_bound.split("][")[0].split(",")[1])

                        if container_start_height >= row_start_height:
                            # print(container_start_height, row_start_height)
                            # print(i.getAttribute("text"), "bad")
                            # result.append(xmlName)
                            bad_xml_map[xmlName] = True
    return bad_xml_map


def print_result(xml_result,all_good):
    has_bad_screen = False
    for xml, result in xml_result.items():
        if result:
            has_bad_screen = True
            print(
                "================== Test failed : Some rows in the screen are off looking==================="
            )
            print(xml)
        else:
            print(
                "================== Test passed : All rows in the screens look good==================="
            )

    if detailed_result and has_bad_screen:
        print("==================DETAILED RESULT===================")
        print(
            "These are the xmls where row starts at the same height as container making the view off "
        )
        # print(result)


def main():
    args = load_arguments()
    data = read_json(os.path.join(args["bugId"], "Execution-12.json"))

    for line in data:
        if "steps" in line:
            listOfSteps = data["steps"]
            print("Look for triggers-------------------")
            # xml_with_off_rows = find_trigger(listOfSteps, args)
            # print_result(xml_with_off_rows)
            rows_xml_map = find_trigger(listOfSteps, args)
            if rows_xml_map:
                print("Found triggers-------------------", len(rows_xml_map))
            else:
                print("No triggers found")
            result = check_container_text_size(rows_xml_map)
            if not result:

            print_result(result)


if __name__ == "__main__":
    main()
