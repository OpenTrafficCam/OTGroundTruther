import helpers.objectstorage as objectstorage
import cv2
from math import atan2, dist, pi
from shapely.geometry import LineString, Polygon


def button_line_switch():
    objectstorage.button_bool["linedetector_toggle"] = not objectstorage.button_bool[
        "linedetector_toggle"
    ]
    print(objectstorage.button_bool["linedetector_toggle"])


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
    # p0 = (objectstorage.maincanvas.points[0][0], objectstorage.maincanvas.points[0][1])
    # p1 = (objectstorage.maincanvas.points[1][0], objectstorage.maincanvas.points[1][1])
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
        (int(major_axis_length), 50),
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
    buffer_around_line = 50

    if objectstorage.button_bool["linedetector_toggle"] is True:

        objectstorage.flow_dict["Detectors"][detector_name] = {
            "type": "line",
            "start_x": objectstorage.maincanvas.points[0][0],
            "start_y": objectstorage.maincanvas.points[0][1],
            "end_x": objectstorage.maincanvas.points[1][0],
            "end_y": objectstorage.maincanvas.points[1][1],
            "color": (200, 125, 125, 255),
            "Geometry_line": LineString(
                [
                    (
                        objectstorage.maincanvas.points[0][0],
                        objectstorage.maincanvas.points[0][1],
                    ),
                    (
                        objectstorage.maincanvas.points[1][0],
                        objectstorage.maincanvas.points[1][1],
                    ),
                ]
            ),
            # USE REAL CALCULATION FOR POLYGON
            "Geometry_polygon": Polygon(
                [
                    (
                        objectstorage.maincanvas.points[0][0] + buffer_around_line,
                        objectstorage.maincanvas.points[0][1] + buffer_around_line,
                    ),
                    (
                        objectstorage.maincanvas.points[0][0] - buffer_around_line,
                        objectstorage.maincanvas.points[0][1] - buffer_around_line,
                    ),
                    (
                        objectstorage.maincanvas.points[1][0] + buffer_around_line,
                        objectstorage.maincanvas.points[1][1] + buffer_around_line,
                    ),
                    (
                        objectstorage.maincanvas.points[1][0] - buffer_around_line,
                        objectstorage.maincanvas.points[1][1] - buffer_around_line,
                    ),
                ],
            ),
        }

    print(objectstorage.flow_dict["Detectors"][detector_name]["Geometry_polygon"])
