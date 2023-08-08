flow_dict = {"sections": [{"id": "S\u00fcd", "type": "line", "relative_offset_coordinates": {"section-enter": {"x": 0.5, "y": 0.5}},
                           "coordinates": [{"x": 43, "y": 184}, {"x": 137, "y": 200}, {"x": 352, "y": 145}, {"x": 362, "y": 89}], "plugin_data": {}}]}


if flow_dict["sections"]:

    for detector in flow_dict["sections"]:
        print(detector)

        if detector["type"] == "line":
            print("ja")
            start_x = detector["coordinates"][0]["x"]
            start_y = detector["coordinates"][0]["y"]
            end_x = detector["coordinates"][1]["x"]
            end_y = detector["coordinates"][1]["y"]
            color = (200, 125, 125, 255)
            print(end_x, end_y, color)

print(bool(flow_dict["sections"]))
