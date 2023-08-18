from math import atan2, dist, pi

import cv2
from shapely.geometry import LineString, Polygon

import helpers.filehelper.objectstorage as objectstorage


def draw_section_line(np_image):
    """_summary_

    Args:
        np_image (_type_): _description_

    Returns:
        _type_: _description_
    """

    return cv2.line(
        np_image,
        (int(objectstorage.maincanvas.points[0][0] * objectstorage.videoobject.x_resize_factor), int(objectstorage.maincanvas.points[0][1] *
         objectstorage.videoobject.y_resize_factor)),

        (int(objectstorage.maincanvas.points[1][0] *
         objectstorage.videoobject.x_resize_factor), int(objectstorage.maincanvas.points[1][1] *
         objectstorage.videoobject.y_resize_factor)),
        (200, 125, 125, 255),
        3,
    )


def draw_ellipse_around_section(np_image, p0, p1):
    middle_point_x = (p0[0] + p1[0]) / 2
    middle_point_y = (p0[1] + p1[1]) / 2

    major_axis_length = dist(p0, p1) / 2

    radian = atan2(
        p1[1] - p0[1],
        p0[0] - p1[0],
    )

    angle = -radian * (180 / pi)

    np_image = cv2.ellipse(
        np_image,
        (int(middle_point_x), int(middle_point_y)),
        (int(major_axis_length), (int(major_axis_length * 0.15))),
        angle,
        0,
        360,
        color=(127, 255, 0, 255),
        thickness=2,
    )

    return np_image


def dump_to_flowdictionary(detector_name):
    """Saves sections to flowdictionary.

    Args:
        canvas (tkinter.canvas): Cancvas that hand out clicked coordinates.
        flow_dict (dictionary): Dictionary with sections and movements.
        detector_name (String): Entrywidgetinput, functions as key of dictionary.
    """
    if objectstorage.config_dict["linedetector_toggle"] is True:
        # original videocoordinates
        x1 = objectstorage.maincanvas.points[0][0]
        y1 = objectstorage.maincanvas.points[0][1]
        x2 = objectstorage.maincanvas.points[1][0]
        y2 = objectstorage.maincanvas.points[1][1]

        print(objectstorage.flow_dict)

        objectstorage.flow_dict["sections"].append({"id": detector_name, "type": "line",
                                                    "relative_offset_coordinates": {"section-enter": {"x": 0.5, "y": 0.5}},
                                                    "coordinates": [{"x": x1, "y": y1}, {"x": x2, "y": y2}], "plugin_data": {}})

