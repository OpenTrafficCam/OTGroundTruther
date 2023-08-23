import tkinter
from math import atan2, dist, pi

import cv2
from more_itertools import pairwise
from PIL import Image, ImageTk

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.config import vehicle_abbreviation
from helpers.filehelper.objectstorage import ELLIPSEHEIGHT
from helpers.resize import get_canvas_coordinate_for


def manipulate_image(np_image=None):
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
        coordinates = row["Crossed_Coordinates"]
        track_id = row["ID"]
        track_class = row["Class"]

        p0_video = coordinates[0]
        np_image = _draw_labelled_circle(np_image, p0_video, str(track_id))

        if len(coordinates) > 1:
            text = f"{str(track_id)}-{vehicle_abbreviation[track_class]}"
            for p0_video, p1_video in pairwise(coordinates):
                np_image = _draw_arrow(
                    np_image=np_image,
                    p0_video=p0_video,
                    p1_video=p1_video,
                    label_text=text,
                )

    return np_image


def _draw_labelled_circle(
    np_image,
    point_video,
    text,
    radius=1,
    color=(0, 255, 255, 255),
    font_scale=1,
):
    point_canvas = get_canvas_coordinate_for(point_video)
    np_image = cv2.circle(np_image, point_canvas, radius, color)
    np_image = cv2.putText(
        np_image,
        text,
        point_canvas,
        cv2.FONT_HERSHEY_SIMPLEX,
        font_scale,
        color,
        1,
        cv2.LINE_AA,
        False,
    )
    return np_image


def _draw_arrow(
    np_image,
    p0_video,
    p1_video,
    color=(255, 185, 15, 255),
    label_text=None,
    font_scale=1,
):
    p0_canvas = get_canvas_coordinate_for(p0_video)
    p1_canvas = get_canvas_coordinate_for(p1_video)
    np_image = cv2.arrowedLine(np_image, p0_canvas, p1_canvas, color, 1)
    if label_text is not None:
        np_image = cv2.putText(
            np_image,
            label_text,
            (
                int((p0_canvas[0] + p1_canvas[0]) / 2),
                int((p0_canvas[1] + p1_canvas[1]) / 2),
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            font_scale,
            color,
            1,
            cv2.LINE_AA,
            False,
        )

    return np_image


def draw_detectors_from_dict(np_image):
    """Draws detectors on every frame.

    Args:
        np_image (numpy_array): image as numpy array

    Returns:
        np_image (numpy_array): returns manipulated image"""

    if objectstorage.flow_dict["sections"]:
        for detector in objectstorage.flow_dict["sections"]:
            for i in range(len(detector["coordinates"]) - 1):
                p0_video, p1_video = _get_detector_video_coordinates(detector, i)
                p0_canvas = get_canvas_coordinate_for(p0_video)
                p1_canvas = get_canvas_coordinate_for(p1_video)
                color = (200, 125, 125, 255)

                np_image = cv2.line(np_image, p0_canvas, p1_canvas, color, 3)

                np_image = draw_ellipse_around_section(
                    np_image, p0=p0_canvas, p1=p1_canvas
                )

    return np_image


def _get_detector_video_coordinates(detector, i):
    p0_video = (
        detector["coordinates"][i]["x"],
        detector["coordinates"][i]["y"],
    )
    p1_video = (
        detector["coordinates"][i + 1]["x"],
        detector["coordinates"][i + 1]["y"],
    )

    return p0_video, p1_video


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
            p0_video = active_count.Coordinates[0]
            np_image = _draw_labelled_circle(
                np_image,
                point_video=p0_video,
                text=str(active_count.ID),
                radius=5,
                color=color,
                font_scale=0.75,
            )

        if len(active_count.Coordinates) > 1:
            for p0_video, p1_video in pairwise(active_count.Coordinates):
                _draw_arrow(
                    np_image=np_image,
                    p0_video=p0_video,
                    p1_video=p1_video,
                    color=(254, 255, 0, 255),
                )

    return np_image


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
        (int(major_axis_length), (int(major_axis_length * ELLIPSEHEIGHT))),
        angle,
        0,
        360,
        color=(127, 255, 0, 255),
        thickness=2,
    )

    return np_image
