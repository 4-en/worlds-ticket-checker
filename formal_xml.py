# formats xml to python dictionary

import xml.etree.ElementTree as ET

def xml_to_dict(element):
    result = {}
    for child in element:
        child_dict = xml_to_dict(child)
        if child_dict:
            if child.tag in result:
                if type(result[child.tag]) is list:
                    result[child.tag].append(child_dict)
                else:
                    result[child.tag] = [result[child.tag], child_dict]
            else:
                result[child.tag] = child_dict
        elif child.text:
            result[child.tag] = child.text
    return result


data = ""
FILENAME = "example_data.xml"

with open(FILENAME, "r") as f:
    data = f.read()

root = ET.fromstring(data)

d = xml_to_dict(root)

for i in d["Table"]:
    print("Name: " + i["SeatGradeName"])
    print("Price: " + i["SalesPrice"])
    print("Availability: " + i["RemainCnt"])
    print()