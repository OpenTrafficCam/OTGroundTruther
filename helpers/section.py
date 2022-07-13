import tkinter.ttk as ttk
import tkinter as tk
import helpers.objectstorage as objectstorage
import cv2
from math import atan2, degrees, radians, dist


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


def draw_ellipse_around_section(np_image):
    middle_point_x = (
        objectstorage.maincanvas.points[0][0] + objectstorage.maincanvas.points[1][0]
    ) / 2
    middle_point_y = (
        objectstorage.maincanvas.points[0][1] + objectstorage.maincanvas.points[1][1]
    ) / 2

    angle = atan2(
        objectstorage.maincanvas.points[0][1] - objectstorage.maincanvas.points[1][1],
        objectstorage.maincanvas.points[0][0] - objectstorage.maincanvas.points[1][0],
    )
    rotation = degrees(angle)

    print(rotation)

    axis_length_x = dist(
        [objectstorage.maincanvas.points[0][0]], [objectstorage.maincanvas.points[1][0]]
    )
    axis_length_y = dist(
        [objectstorage.maincanvas.points[0][1]], [objectstorage.maincanvas.points[1][1]]
    )

    center_coordinates = (int(middle_point_x), int(middle_point_y))

    axesLength = (int(axis_length_x), int(axis_length_y))

    startAngle = 0

    endAngle = 360

    # Red color in BGR
    color = (0, 0, 255)

    # Line thickness of 5 px
    thickness = 2

    # Using cv2.ellipse() method
    # Draw a ellipse with red line borders of thickness of 5 px
    return cv2.ellipse(
        np_image,
        center_coordinates,
        axesLength,
        rotation,
        startAngle,
        endAngle,
        color,
        thickness,
    )


def dump_to_flowdictionary(detector_name):
    """Saves sections to flowdictionary.

    Args:
        canvas (tkinter.canvas): Cancvas that hand out clicked coordinates.
        flow_dict (dictionary): Dictionary with sections and movements.
        detector_name (String): Entrywidgetinput, functions as key of dictionary.
    """

    if objectstorage.button_bool["linedetector_toggle"] is True:

        objectstorage.flow_dict["Detectors"][detector_name] = {
            "type": "line",
            "start_x": objectstorage.maincanvas.points[0][0],
            "start_y": objectstorage.maincanvas.points[0][1],
            "end_x": objectstorage.maincanvas.points[1][0],
            "end_y": objectstorage.maincanvas.points[1][1],
            "color": (200, 125, 125, 255),
        }