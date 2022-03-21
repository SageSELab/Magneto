import xml.etree.ElementTree as ET


def main():
    root = ET.parse('25.xml').getroot()

    for tag in root.iter('node'):
        t_value = tag.get('text')
        if t_value: # is not None or "": #to filter empty text fields
            print(t_value)

def readTextInXml(xmlName):
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


if __name__ == "__main__":
    main()
