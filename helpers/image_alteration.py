import tkinter

import cv2
from more_itertools import pairwise
from PIL import Image, ImageTk

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.config import vehicle_abbreviation
from helpers.section import draw_ellipse_around_section, draw_section_line


def manipulate_image(np_image=None):
    if np_image is None:
        np_image = objectstorage.videoobject.np_image.copy()

    if objectstorage.config_dict["linedetector_toggle"]:

        np_image = draw_section_line(np_image)
        np_image = draw_ellipse_around_section(
            np_image,
            p0=(
                (objectstorage.maincanvas.points[0][0] *
                    objectstorage.videoobject.x_resize_factor),
                (objectstorage.maincanvas.points[0][1] *
                    objectstorage.videoobject.y_resize_factor),
            ),
            p1=(
                (objectstorage.maincanvas.points[1][0] *
                    objectstorage.videoobject.x_resize_factor),
                (objectstorage.maincanvas.points[1][1] *
                    objectstorage.videoobject.y_resize_factor),
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
        _type_: altered numpy array as image with drawn finished counts
    """
    # subset background dic when frames match
    if objectstorage.ground_truth.empty:
        return np_image

    current_frame = objectstorage.videoobject.current_frame

    objectstorage.ground_truth["First_Frame"] = objectstorage.ground_truth[
        "Crossed_Frames"
    ].str[0]
    objectstorage.ground_truth["Last_Frame"] = objectstorage.ground_truth[
        "Crossed_Frames"
    ].str[-1]

    # dataframe faster than looping through dictionary
    df_subset = objectstorage.ground_truth.loc[
        (objectstorage.ground_truth["First_Frame"] <= current_frame)
        & (objectstorage.ground_truth["Last_Frame"] >= current_frame)
    ]

    for index, row in df_subset.iterrows():
        try:
            coordinates = row["Crossed_Coordinates"]
            track_id = row["ID"]
            track_class = row["Class"]

            np_image = cv2.circle(
                np_image,
                (
                    int(coordinates[0][0] *
                        objectstorage.videoobject.x_resize_factor),
                    int(coordinates[0][1] *
                        objectstorage.videoobject.y_resize_factor),
                ),
                5,
                (0, 255, 255, 255),
            )
            np_image = cv2.putText(
                np_image,
                str(track_id),
                (
                    int(coordinates[0][0] *
                        objectstorage.videoobject.x_resize_factor),
                    int(coordinates[0][1] *
                        objectstorage.videoobject.y_resize_factor),
                ),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 255, 255, 255),
                1,
                cv2.LINE_AA,
                False,
            )
            # draw line if track consists of more than one coordinate and name of the class
            if len(coordinates) > 1:
                for coordinate_start, coordinate_end in pairwise(coordinates):
                    np_image = cv2.arrowedLine(
                        np_image,
                        (int(coordinate_start[0] * objectstorage.videoobject.x_resize_factor),
                         int(coordinate_start[1] * objectstorage.videoobject.y_resize_factor)),
                        (int(coordinate_end[0] * objectstorage.videoobject.x_resize_factor),
                         int(coordinate_end[1] * objectstorage.videoobject.y_resize_factor)),
                        (255, 185, 15, 255),
                        1,
                    )
                    np_image = cv2.putText(
                        np_image,
                        str(track_id) + "-"+vehicle_abbreviation[track_class],
                        (
                            int((coordinate_start[0] + coordinate_end[0])/2*
                                objectstorage.videoobject.x_resize_factor),
                            int((coordinate_start[1] + coordinate_end[1])/2*
                                objectstorage.videoobject.y_resize_factor),
                        ),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.4,
                        (255, 185, 15, 255),
                        1,
                        cv2.LINE_AA,
                        False,
                    )
                
                
        except Exception:
            continue
    return np_image


def draw_detectors_from_dict(np_image):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if objectstorage.flow_dict["sections"]:

        for detector in objectstorage.flow_dict["sections"]:
            if detector["type"] == "line":
                # resize to videowidth and height
                start_x = int(detector["coordinates"][0]["x"] *
                              objectstorage.videoobject.x_resize_factor)
                start_y = int(detector["coordinates"][0]["y"] *
                              objectstorage.videoobject.y_resize_factor)
                end_x = int(detector["coordinates"][1]["x"] *
                            objectstorage.videoobject.x_resize_factor)
                end_y = int(detector["coordinates"][1]["y"] *
                            objectstorage.videoobject.y_resize_factor)
                color = (200, 125, 125, 255)

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

        if active_count.Coordinates:
            np_image = cv2.circle(
                np_image,
                (int(active_count.Coordinates[0][0] * objectstorage.videoobject.x_resize_factor),
                 int(active_count.Coordinates[0][1] * objectstorage.videoobject.y_resize_factor)),
                5,
                color,
            )
            np_image = cv2.putText(
                np_image,
                str(active_count.ID),
                (int(active_count.Coordinates[0][0] * objectstorage.videoobject.x_resize_factor),
                 int(active_count.Coordinates[0][1] * objectstorage.videoobject.y_resize_factor)),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.75,
                color,
                1,
                cv2.LINE_AA,
                False,
            )
        # draw line when count has two coordinates
        if len(active_count.Coordinates) > 1:
            for coordinate_start, coordinate_end in pairwise(active_count.Coordinates):

                np_image = cv2.arrowedLine(
                    np_image,
                    (int(coordinate_start[0] * objectstorage.videoobject.x_resize_factor),
                     int(coordinate_start[1] * objectstorage.videoobject.y_resize_factor)),
                    (int(coordinate_end[0] * objectstorage.videoobject.x_resize_factor),
                     int(coordinate_end[1] * objectstorage.videoobject.y_resize_factor)),
                    (254, 255, 0, 255),
                    1,
                )

    return np_image
