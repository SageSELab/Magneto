import sys
import xml.etree.ElementTree as ET
from xml.dom import minidom

from lxml import etree  # as lxmlEt


def main():
    root = ET.parse("18.xml").getroot()

    for tag in root.iter("node"):
        t_value = tag.get("text")
        if t_value:  # is not None or "": #to filter empty text fields
            print(t_value)


def readXML(xmlFile):
    try:
        tree = ET.parse(xmlFile)
        # get root element
        root = tree.getroot()
        return root
    except FileNotFoundError as f:
        # print(xmlFile,"File not found!")
        return

def readBoundOfFocusedElement(xmlFile):
    try:
        tree = ET.parse(xmlFile)
        # get root element
        root = tree.getroot()
        for tag in root.iter("node"):
            b = tag.get("bounds")
            start = b.split("][")[0].replace("[", "")
            end = b.split("][")[1].replace("]", "")
            startX = start.split(",")[0]
            startY = start.split(",")[1]
            endX = end.split(",")[0]
            endY = end.split(",")[1]
            # return
            break
        return ','.join((startX,startY, endX,endY))
    except FileNotFoundError as f:
        # print(xmlFile,"File not found!")
        return

def readTextInXml(xmlName):
    """Reads all text field in xml and returns a list all text"""
    try:
        root = ET.parse(xmlName).getroot()
        textList = []
        for tag in root.iter("node"):
            t_value = tag.get("text")
            if t_value:  # is not None or "": #to filter empty text fields
                # print(t_value)
                textList.append(t_value)
        return textList
    except:
        print("No xml", xmlName)


def return_resource_id_of_image(xmlName):
    """Reads all imageView in xml and returns a list of their resource-ids"""
    try:
        root = ET.parse(xmlName).getroot()
        image_resources = []
        counter = 0
        for tag in root.iter("node"):
            className = tag.get("class")
            id = tag.get("resource-id")
            if not id:  # for valid nodes with no id
                id = tag.get("content-desc")
            if not id:
                id = str(counter)
                counter += 1
            if (
                className == "android.widget.ImageView"
            ):  # is not None or "": #to filter empty text fields
                # print(t_value)
                image_resources.append(id)
        return image_resources
    except:
        print("No xml", xmlName)


def return_resource_id_with_text(xmlName):
    """Reads all text field in xml and returns a map of resource-id and text"""
    try:
        root = ET.parse(xmlName).getroot()
        text_resource_map = {}
        counter = 0
        for tag in root.iter("node"):
            t_value = tag.get("text")
            id = tag.get("resource-id")
            if not id:
                id = str(counter)
                counter += 1
            if t_value:  # is not None or "": #to filter empty text fields
                # print(t_value)
                text_resource_map[id] = t_value
        return text_resource_map
    except:
        print("No xml", xmlName)


def readUserFieldTextInXml(xmlName):
    """Reads only user entered text field and returns a map of resource-id and text"""
    try:
        root = ET.parse(xmlName).getroot()
        text_resource_map = {}
        counter = 0
        for tag in root.iter("node"):
            if tag.attrib["class"] == "android.widget.EditText":
                t_value = tag.get("text")
                id = tag.get("resource-id")
                if not id:
                    id = str(counter)
                    counter += 1
                if not t_value:
                    t_value = ""
                # if t_value: # is not None or "": #to filter empty text fields
                # print(t_value)
                text_resource_map[id] = t_value
        return text_resource_map
    except Exception as e:
        print(e)
        print("No xml", xmlName)


def findParentBoundOfMatchingNode(xmlName, listOfTriggerWords):
    """Reads only text field and returns their parent node"""
    # try:
    root = etree.parse(xmlName).getroot()
    for tag in root.iter("node"):
        t_value = tag.get("text")
        # if ["theme", "night"] in t_value.lower():
        if any(words in t_value.lower() for words in listOfTriggerWords):
            p = tag.getparent()
            # [42,306][874,498]
            allBounds = p.get("bounds")
            if allBounds:
                start = allBounds.split("][")[0].replace("[", "")
                end = allBounds.split("][")[1].replace("]", "")
                startX = start.split(",")[0]
                startY = start.split(",")[1]
                endX = end.split(",")[0]
                endY = end.split(",")[1]
                return startY, endY
            else:
                return "-1", "-1"
    return "-1", "-1"

    # except Exception as e:
    #     # print(e.__cause__)
    #     print("No xml", xmlName)
    #     return -1, -1

    # root = ET.parse(xmlName).getroot()
    # text_resource_map = {}
    # counter = 0
    # # t = root.findall("node")
    # # print(len(t))
    # # for x in t:
    # #     # print(x.get("bounds"), "THIS?")
    # #     if "theme" in x.get("text").lower():
    # # bounds="[42,306][874,498]"><
    # for tag in root.iter("node"):
    #     t_value = tag.get("text")
    #     # print("TEXT", t_value)
    #     if "theme" in t_value.lower():
    #         # find parent
    #         print("FOUND=========", tag, t_value)
    #         p = tag.getparent()
    #         print(p, "-----BOOM-----")

    #     return True
    # except Exception as e:
    #     print(e)
    #     print("No xml", xmlName)


def find_recycler_class(xmlName, list_of_recycle_classes, list_of_container_classes):
    """Finds rows by looking for container in recycler class and checks if row start height is lower than container or not
    This solves issues like that of bug 121"""
    tree = minidom.parse(xmlName)
    all_nodes = tree.getElementsByTagName("node")
    result = []
    for parent_nodes in all_nodes:
        if parent_nodes.getAttribute("class") in list_of_recycle_classes:
            children = parent_nodes.getElementsByTagName("node")
            for child in children:
                # print(type(child))
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
                            result.append(xmlName)
                        # else:
                        #     print(i.getAttribute("text"), "ok")
            # sys.exit()
            print(set(result))
            return result


def find_recycler_class_only(xmlName, list_of_recycle_classes):
    """Finds if there are rows by looking for nodes that have recycler class"""
    tree = minidom.parse(xmlName)
    all_nodes = tree.getElementsByTagName("node")
    result = []
    for parent_nodes in all_nodes:
        if parent_nodes.getAttribute("class") in list_of_recycle_classes:
            children = parent_nodes.getElementsByTagName("node")
            result.append(children)

            # else:
            #     print(i.getAttribute("text"), "ok")
            # sys.exit()
    return result


if __name__ == "__main__":
    main()

# for tag in root_node.findall('node/node'):
#     # Get the value of the heading attribute
#     # h_value = tag.get('heading')
#     # if h_value is not None:
#     #     print(h_value)
#     # Get the value of the text attribute
#     t_value = tag.get('text')
#     if t_value is not None:
#         print(t_value)
