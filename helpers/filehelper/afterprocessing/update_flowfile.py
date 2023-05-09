import json
import cv2
import os
import re

PATH__LOAD_FLOWFILE = r"\\vs-grp08.zih.tu-dresden.de\otc_live\validate\ground truth events\Sections\Knotenpunkte\Aachen_15.otflow"
PATH__SAFE_FLOWFILE = r"\\vs-grp08.zih.tu-dresden.de\otc_live\validate\ground truth events\Sections\updated_sections\Aachen_15.otflow"

PATH_VIDEOFILE = r"\\vs-grp08.zih.tu-dresden.de\otc_live\validate\ground truth events\Videos\Aachen\Aachen_OTCamera15_FR20_2022-11-15_15-00-00.mp4"

file_name_with_extension = os.path.basename(PATH_VIDEOFILE)
file_name_without_extension, file_extension = os.path.splitext(file_name_with_extension)

#finde cityname with regex

pattern = r'([A-Za-z]+)_OT([A-Za-z]+)(\d+)_.*'
match = re.match(pattern, file_name_without_extension)
if match:
    name = match.group(1)
    otcamera = match.group(2) + match.group(3)
    city_otcamera = name + "_" + otcamera


#open stream
stream = cv2.VideoCapture(PATH_VIDEOFILE)

#get video width and height
videowidth = stream.get(cv2.CAP_PROP_FRAME_WIDTH)
videoheight = stream.get(cv2.CAP_PROP_FRAME_HEIGHT)

#height/width of gui
width = 800
height=600

#calculate resize-factor
y_resize_factor = height / videoheight
x_resize_factor = width / videowidth


#load flowfile
flowfile = open(PATH__LOAD_FLOWFILE, "r")
flowfile = flowfile.read()

flow_dict = json.loads(flowfile)



#updating flowfile with new section coordinates
for detector in flow_dict["Detectors"]:
    x1 = int(flow_dict["Detectors"][detector]["start_x"] / x_resize_factor)
    y1 = int(flow_dict["Detectors"][detector]["start_y"] / y_resize_factor)
    x2 = int(flow_dict["Detectors"][detector]["end_x"] / x_resize_factor)
    y2 = int(flow_dict["Detectors"][detector]["end_y"] / y_resize_factor)

    #assigning to flowfile
    flow_dict["Detectors"][detector]["start_x"] = x1
    flow_dict["Detectors"][detector]["start_y"] = y1
    flow_dict["Detectors"][detector]["end_x"] = x2
    flow_dict["Detectors"][detector]["end_y"] = y2

#overwrite flowdict with with right order of things
#create empty new dic
new_flow_dict = {}

#defined metadatadic
meta_data_dict = {"metadata":{"software": "OTGroundTruther",
		 "version" : "0.1.0",
		 "video"   : {"name": city_otcamera,
		 	      "width"   : videowidth,
			      "height"  : videoheight,
		}}}
#use defined dic to update empty new dic ==> to get right order 
new_flow_dict.update(meta_data_dict)
new_flow_dict.update(flow_dict)

#safe flowfile
with open(PATH__SAFE_FLOWFILE, 'w') as f:
    json.dump(new_flow_dict, f, indent=4)



