from PIL import Image, ImageTk
import helpers.objectstorage as objectstorage
import tkinter
import cv2
from helpers.section import draw_section_line, draw_ellipse_around_section
import numpy as np


def manipulate_image(np_image=None):
    if np_image is None:
        np_image = objectstorage.videoobject.np_image.copy()

    if objectstorage.active_countings:

        np_image = draw_active_count(
            np_image,
        )

    if objectstorage.button_bool["linedetector_toggle"]:

        np_image = draw_section_line(np_image)
        np_image = draw_ellipse_around_section(
            np_image,
            p0=(
                objectstorage.maincanvas.points[0][0],
                objectstorage.maincanvas.points[0][1],
            ),
            p1=(
                objectstorage.maincanvas.points[1][0],
                objectstorage.maincanvas.points[1][1],
            ),
        )

    np_image = draw_detectors_from_dict(np_image)

    np_image = draw_finished_counts(np_image)

    np_image = draw_tag_around_start_coordinate(np_image)

    image = Image.fromarray(np_image)  # to PIL format

    objectstorage.videoobject.ph_image = ImageTk.PhotoImage(image)

    objectstorage.maincanvas.create_image(
        0, 0, anchor=tkinter.NW, image=objectstorage.videoobject.ph_image
    )

    objectstorage.maincanvas.update()


def draw_finished_counts(np_image):
    """Subsets dictionary with finished counts. Dictionary contains all counts
    that that occur in current frame.

    Args:
        np_image (_type_): numpy array as image to draw lines on

    Returns:
        _type_: altered numpy array as image
    """
    # subset background dic when frames match
    # if not objectstorage.background_dic:
    #     return np_image
    current_frame = objectstorage.videoobject.current_frame
    d = objectstorage.background_dic

    background_dic_subset = {
        k: v
        for k, v in d.items()
        if v["Entry_Frame"] <= current_frame and v["Exit_Frame"] >= current_frame
    }

    for object_id in background_dic_subset:

        if background_dic_subset[object_id]["GT_Type"] == "Line":

            np_image = cv2.line(
                np_image,
                background_dic_subset[object_id]["Entry_Coordinate"],
                background_dic_subset[object_id]["Exit_Coordinate"],
                (200, 125, 125, 255),
                3,
            )

        else:
            pts = np.array(
                background_dic_subset[object_id]["All_Coordinates"],
                np.int32,
            )

            pts = pts.reshape((-1, 1, 2))
            np_image = cv2.polylines(
                np_image,
                [pts],
                isClosed=False,
                color=(200, 125, 125, 255),
                thickness=2,
            )

            np_image = cv2.circle(
                np_image,
                (
                    background_dic_subset[object_id]["Entry_Coordinate"][0],
                    background_dic_subset[object_id]["Entry_Coordinate"][1],
                ),
                5,
                (0, 255, 255, 255),
            )
            np_image = cv2.putText(
                np_image,
                str(background_dic_subset[object_id]["ID"]),
                (
                    background_dic_subset[object_id]["Entry_Coordinate"][0],
                    background_dic_subset[object_id]["Entry_Coordinate"][1],
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255, 255),
                1,
                cv2.LINE_AA,
                False,
            )

    return np_image


def draw_active_count(np_image):
    for active_count in objectstorage.active_countings:
        # active_count = objectstorage.active_countings[objectstorage.active_countings_index]
        if active_count.Type != "Line" and len(active_count.All_Coordinates) >= 2:
            # Polygon corner points coordinates
            pts = np.array(
                active_count.All_Coordinates,
                np.int32,
            )

            pts = pts.reshape((-1, 1, 2))
            np_image = cv2.polylines(
                np_image,
                [pts],
                isClosed=False,
                color=(200, 125, 125, 255),
                thickness=2,
            )
            np_image = cv2.arrowedLine(
                np_image,
                (
                    active_count.All_Coordinates[-2][0],
                    active_count.All_Coordinates[-2][1],
                ),
                (
                    active_count.All_Coordinates[-1][0],
                    active_count.All_Coordinates[-1][1],
                ),
                color=(200, 125, 125, 255),
                thickness=2,
                tipLength=0.1,
            )
        elif active_count.Exit_Coordinate and not active_count.first_coordinate:
            np_image = cv2.line(
                np_image,
                active_count.Entry_Coordinate,
                active_count.Exit_Coordinate,
                (200, 125, 125, 255),
                2,
            )
    return np_image


def draw_detectors_from_dict(np_image):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if objectstorage.flow_dict["Detectors"]:

        for detector in objectstorage.flow_dict["Detectors"]:
            if objectstorage.flow_dict["Detectors"][detector]["type"] == "line":
                start_x = objectstorage.flow_dict["Detectors"][detector]["start_x"]
                start_y = objectstorage.flow_dict["Detectors"][detector]["start_y"]
                end_x = objectstorage.flow_dict["Detectors"][detector]["end_x"]
                end_y = objectstorage.flow_dict["Detectors"][detector]["end_y"]
                color = objectstorage.flow_dict["Detectors"][detector]["color"]

                np_image = cv2.line(
                    np_image, (start_x, start_y), (end_x, end_y), color, 3
                )

                np_image = draw_ellipse_around_section(
                    np_image, p0=(start_x, start_y), p1=(end_x, end_y)
                )

    return np_image


def draw_tag_around_start_coordinate(np_image):
    for active_count in objectstorage.active_countings:
        if (
            active_count
            != objectstorage.active_countings[objectstorage.active_countings_index]
        ):
            color = (0, 0, 255, 255)
        else:
            color = (124, 252, 0, 255)

        if active_count.Entry_Coordinate is not None:
            np_image = cv2.circle(
                np_image,
                (active_count.Entry_Coordinate[0], active_count.Entry_Coordinate[1]),
                5,
                color,
            )
            np_image = cv2.putText(
                np_image,
                str(active_count.ID),
                (active_count.Entry_Coordinate[0], active_count.Entry_Coordinate[1]),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                color,
                1,
                cv2.LINE_AA,
                False,
            )
    return np_image
