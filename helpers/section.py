import helpers.filehelper.objectstorage as objectstorage
import cv2
from math import atan2, dist, pi
from shapely.geometry import LineString, Polygon



def draw_section_line(np_image):
    """_summary_

    Args:
        np_image (_type_): _description_

    Returns:
        _type_: _description_
    """
    return cv2.line(
        np_image,
        objectstorage.maincanvas.points[0],
        objectstorage.maincanvas.points[1],
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
        (int(major_axis_length), (int(major_axis_length*0.15))),
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

        x1 = objectstorage.maincanvas.points[0][0]
        y1 = objectstorage.maincanvas.points[0][1]
        x2 = objectstorage.maincanvas.points[1][0]
        y2 = objectstorage.maincanvas.points[1][1]

        objectstorage.flow_dict["Detectors"][detector_name] = {
            "type": "line",
            "start_x": x1,
            "start_y": y1,
            "end_x": x2,
            "end_y": y2,
            "color": (200, 125, 125, 255),
            "Geometry_line": shapely_object(x1, y1, x2, y2, linestring=True),
            # USE REAL CALCULATION FOR POLYGON
            # "Geometry_polygon": shapely_object(x1, y1, x2, y2),
        }


def shapely_object(x1, y1, x2, y2, linestring=False, buffer=50):
    if linestring:
        return LineString([(x1, y1), (x2, y2)])
    else:
        return Polygon(
            [
                (x1 + buffer, y1 + buffer),
                (x1 - buffer, y1 - buffer),
                (x2 + buffer, y2 + buffer),
                (x2 - buffer, y2 - buffer),
            ]
        )
