from PIL import Image, ImageTk
import helpers.objectstorage as objectstorage
import tkinter
import cv2
from helpers.section import draw_section_line, draw_ellipse_around_section


def manipulate_image(np_image=None):
    # TODO create lines from coordinates and frame / current frame
    if np_image is None:
        np_image = objectstorage.videoobject.np_image.copy()

    if objectstorage.active_countings:

        np_image = draw_active_count(np_image, objectstorage.active_countings[0])

    if objectstorage.button_bool["linedetector_toggle"]:

        np_image = draw_section_line(np_image)
        np_image = draw_ellipse_around_section(np_image)

    np_image = draw_detectors_from_dict(np_image)

    np_image = draw_finished_counts(np_image)

    image = Image.fromarray(np_image)  # to PIL format

    objectstorage.videoobject.ph_image = ImageTk.PhotoImage(image)

    objectstorage.maincanvas.create_image(
        0, 0, anchor=tkinter.NW, image=objectstorage.videoobject.ph_image
    )

    objectstorage.maincanvas.update()

    # print(objectstorage.flow_dict)


def draw_finished_counts(np_image):
    """Subsets dictionary with finished counts. Dictionary contains all counts
    that that occur in current frame.

    Args:
        np_image (_type_): numpy array as image to draw lines on

    Returns:
        _type_: altered numpy array as image
    """
    # subset background dic when frames match
    current_frame = objectstorage.videoobject.current_frame
    d = objectstorage.background_dic

    background_dic_subset = {
        k: v
        for k, v in d.items()
        if v["Entry_Frame"] <= current_frame and v["Exit_Frame"] >= current_frame
    }

    for object_id in background_dic_subset:

        np_image = cv2.line(
            np_image,
            background_dic_subset[object_id]["Entry_Coordinate"],
            background_dic_subset[object_id]["Exit_Coordinate"],
            (200, 125, 125, 255),
            3,
        )
    return np_image


def draw_active_count(np_image, active_count=None):

    if active_count.Exit_Coordinate and not active_count.first_coordinate:

        return cv2.line(
            np_image,
            active_count.Entry_Coordinate,
            active_count.Exit_Coordinate,
            (200, 125, 125, 255),
            3,
        )
    else:
        print("current count not drawn!")
        return np_image


def draw_detectors_from_dict(np_image):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if objectstorage.flow_dict["Detectors"]:

        for detector in objectstorage.flow_dict["Detectors"]:
            # if objectstorage.flow_dict["Detectors"][detector]["type"] == Line:
            start_x = objectstorage.flow_dict["Detectors"][detector]["start_x"]
            start_y = objectstorage.flow_dict["Detectors"][detector]["start_y"]
            end_x = objectstorage.flow_dict["Detectors"][detector]["end_x"]
            end_y = objectstorage.flow_dict["Detectors"][detector]["end_y"]
            color = objectstorage.flow_dict["Detectors"][detector]["color"]

            np_image = cv2.line(np_image, (start_x, start_y), (end_x, end_y), color, 3)

    return np_image
