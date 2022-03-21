import xml.etree.ElementTree as ET


def main():
    root = ET.parse('18.xml').getroot()

    for tag in root.iter('node'):
        t_value = tag.get('text')
        if t_value: # is not None or "": #to filter empty text fields
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

def readTextInXml(xmlName):
    '''Reads all text field in xml and returns a list all text'''
    try:
        root = ET.parse(xmlName).getroot()
        textList = []
        for tag in root.iter('node'):
            t_value = tag.get('text')
            if t_value: # is not None or "": #to filter empty text fields
                # print(t_value)
                textList.append(t_value)
        return textList
    except:
        print("No xml",xmlName)

def return_resource_id_of_image(xmlName):
    '''Reads all imageView in xml and returns a list of their resource-ids'''
    try:
        root = ET.parse(xmlName).getroot()
        image_resources = []
        counter =0
        for tag in root.iter('node'):
            className = tag.get('class')
            id = tag.get('resource-id')
            if not id:              #for valid nodes with no id
                id = tag.get('content-desc')
            if not id:
                id=str(counter)
                counter+=1
            if className == 'android.widget.ImageView': # is not None or "": #to filter empty text fields
                # print(t_value)
                image_resources.append(id)
        return image_resources
    except:
        print("No xml",xmlName)

def return_resource_id_with_text(xmlName):
    '''Reads all text field in xml and returns a map of resource-id and text '''
    try:
        root = ET.parse(xmlName).getroot()
        text_resource_map = {}
        counter =0
        for tag in root.iter('node'):
            t_value = tag.get('text')
            id = tag.get('resource-id')
            if not id:
                id = str(counter)
                counter+=1
            if t_value: # is not None or "": #to filter empty text fields
                # print(t_value)
                text_resource_map[id]=t_value
        return text_resource_map
    except:
        print("No xml",xmlName)

def readUserFieldTextInXml(xmlName):
    '''Reads only user entered text field and returns a map of resource-id and text'''
    try:
        root = ET.parse(xmlName).getroot()
        text_resource_map = {}
        counter=0
        for tag in root.iter('node'):
            if tag.attrib['class'] == 'android.widget.EditText':
                t_value = tag.get('text')
                id = tag.get('resource-id')
                if not id:
                    id = str(counter)
                    counter+=1
                if not t_value:
                    t_value=''
                # if t_value: # is not None or "": #to filter empty text fields
                    # print(t_value)
                text_resource_map[id]=t_value
        return text_resource_map
    except Exception as e:
        print(e)
        print("No xml",xmlName)


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
