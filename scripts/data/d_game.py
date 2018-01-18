

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

# tree = ET.parse(os.path.abspath('d_config.xml'))
#
# root = tree.getroot()
#
# for child in root:
#     print(child.find('base').text)