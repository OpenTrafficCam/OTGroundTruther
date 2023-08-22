import tkinter as tk
from math import atan2, dist

import numpy as np

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.objectstorage import ELLIPSEHEIGHT
from helpers.image_alteration import manipulate_image


class OtcCanvas(tk.Canvas):
    """_summary_

    Args:
        tk (_type_): _description_
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def click_receive_vehicle_coordinates(self, event):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event (tkinter.event): Click on canvas triggers event.
            list_index (index):
        """
        self.coordinateX = int(
            self.canvasx(event.x) / objectstorage.videoobject.x_resize_factor
        )
        self.coordinateY = int(
            self.canvasy(event.y) / objectstorage.videoobject.y_resize_factor
        )

        self._handle_event(event)

        self.update_image()

    def update_image(self):
        manipulate_image(objectstorage.videoobject.np_image.copy())

    def _handle_event(self, event):
        """depending on left or right mousclick and if click is in section
        coorindates get added, reseted or initialized
        """
        if not objectstorage.flow_dict["sections"]:
            return
        in_detector_ellipse = False
        for detector in objectstorage.flow_dict["sections"]:
            for i in range(len(detector["coordinates"]) - 1):
                p0 = (
                    detector["coordinates"][i]["x"],
                    detector["coordinates"][i]["y"],
                )
                p1 = (
                    detector["coordinates"][i + 1]["x"],
                    detector["coordinates"][i + 1]["y"],
                )

                if self._coordinate_in_section_ellipse(
                    section_p0=p0, section_p1=p1
                ):
                    print(f"Coordinate in the gate: {detector}")

                    if (not self._there_is_an_active_count() or (
                        self._there_is_an_active_count()
                        and not self._is_same_gate_as_before(detector)
                    )):
                        self._append_new_event(detector)

                    elif (self._there_is_an_active_count() and
                          self._is_same_gate_as_before(detector)
                          ):
                        self._update_event()
                    in_detector_ellipse = True
                    break
            if in_detector_ellipse:
                break

    def _append_new_event(self, detector):
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Gates.append(detector["id"])
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Coordinates.append((self.coordinateX, self.coordinateY))
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Frames.append(objectstorage.videoobject.current_frame)

    def _update_event(self):
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Coordinates[-1] = (
            self.coordinateX,
            self.coordinateY,
        )
        objectstorage.active_countings[objectstorage.active_countings_index].Frames[
            -1
        ] = objectstorage.videoobject.current_frame

    def _delete_event(self):
        objectstorage.active_countings[objectstorage.active_countings_index].Gates = []
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Coordinates = []
        objectstorage.active_countings[objectstorage.active_countings_index].Frames = []

    def _coordinate_in_section_ellipse(self, section_p0, section_p1):
        section_middle_point_x = (section_p0[0] + section_p1[0]) / 2
        section_middle_point_y = (section_p0[1] + section_p1[1]) / 2
        x = self.coordinateX - section_middle_point_x
        # mirror the y-values because the y-axis in the frame is mirrored
        y = -self.coordinateY + section_middle_point_y
        radian = atan2(section_p1[1] - section_p0[1], section_p0[0] - section_p1[0])
        a = dist(section_p0, section_p1) / 2
        b = a * ELLIPSEHEIGHT
        # turned ellipse equation
        return (x * np.cos(radian) + y * np.sin(radian)) ** 2 / a**2 + (
            x * np.sin(radian) - y * np.cos(radian)
        ) ** 2 / b**2 <= 1

    def _there_is_an_active_count(self):
        return (
            len(
                objectstorage.active_countings[
                    objectstorage.active_countings_index
                ].Gates
            )
            > 0
        )

    def _is_same_gate_as_before(self, detector):
        return (
            objectstorage.active_countings[objectstorage.active_countings_index].Gates[
                -1
            ]
            == detector["id"]
        )


class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(fill="x")

        objectstorage.maincanvas = OtcCanvas(
            master=self.frame_canvas, width=0, height=0
        )
        objectstorage.maincanvas.pack()
