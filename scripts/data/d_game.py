

d_games = {
    "DdzGame":
        {
            "sign": "Ddz",
            "hallCount": 4,
            "open": 1  # 0为不开放，大于0为开放
        },

    "ZjhGame":
        {
            "sign": "Zjh",
            "hallCount": 4,
            "open": 1  # 0为不开放，大于0为开放
        }
}


import xml.etree.ElementTree as ET
import os

# dom = xml.dom.minidom.parse(os.path.abspath('d_config.xml'))
#
# root = dom.documentElement
# # taxRate = root.getElementsByTagName('zjh')[0].getAttribute('taxRate')
# zjh = root.getElementsByTagName('zjh')[0]
# taxRate = zjh.getElementsByTagName('taxRate')[0]
# gold = 100
# result = gold * float(taxRate.data)

# print(taxRate.data)

tree = ET.parse(os.path.abspath('d_config.xml'))

root = tree.getroot()

for child in root:
    print((float(child.attrib['taxRate']) * 10))