import tkinter as tk
from tkinter import messagebox
import helpers.objectstorage as objectstorage
from helpers.objectstorage import active_countings, button_bool

from helpers.image_alteration import manipulate_image


class OtcCanvas(tk.Canvas):
    """_summary_

    Args:
        tk (_type_): _description_
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.points = [(0, 0), (0, 0)]
        self.polygon_points = []

        self.bind(
            "<B1-Motion>",
            lambda event: [
                self.click_receive_section_coordinates(event, 1),
            ],
        )
        self.bind(
            "<Button-2>",
            lambda event: [
                self.undo_active_count_coords(event),
            ],
        )

    def click_receive_section_coordinates(self, event, list_index):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event (tkinter.event): Click on canvas triggers event.
            list_index (index):
        """
        if button_bool["linedetector_toggle"]:
            #  uses mouseevents to get coordinates (left button)
            self.coordinateX = int(self.canvasx(event.x))
            self.coordinateY = int(self.canvasy(event.y))

            self.points[list_index] = (
                self.coordinateX,
                self.coordinateY,
            )
            # section line gets drawn when second section coordinate is
            # changed/else Line jumps
            if list_index == 1:
                manipulate_image(objectstorage.videoobject.np_image.copy())

    def click_receive_vehicle_coordinates(self, event):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event (tkinter.event): Click on canvas triggers event.
            list_index (index):
        """
        if button_bool["linedetector_toggle"]:
            return
        if not objectstorage.active_countings:
            messagebox.showinfo(
                title="Info",
                message="First create empty count with hotkey n",
            )
            return
        active_count = objectstorage.active_countings[
            objectstorage.active_countings_index
        ]

        # uses mouseevents to get coordinates (left button)
        self.coordinateX = int(self.canvasx(event.x))
        self.coordinateY = int(self.canvasy(event.y))

        if button_bool["gt_active"]:
            # active_count.Type = "Line"
            if not active_count.First_Coordinate:

                active_count.Entry_Coordinate = (
                    self.coordinateX,
                    self.coordinateY,
                )
                active_countings[
                    objectstorage.active_countings_index
                ].Entry_Frame = objectstorage.videoobject.current_frame
                active_count.First_Coordinate = True

            else:
                active_count.Exit_Coordinate = (
                    self.coordinateX,
                    self.coordinateY,
                )
                active_count.Exit_Frame = objectstorage.videoobject.current_frame
                active_count.First_Coordinate = False

            manipulate_image(objectstorage.videoobject.np_image.copy())

            objectstorage.active_countings[
                objectstorage.active_countings_index
            ].get_intersect_and_frame(self)

    def delete_points(self):
        """delete list of polygon points after scrolling, sliding, playing, rewinding"""

        if self.polygon_points:
            self.polygon_points = []
        else:
            self.points = [(0, 0), (0, 0)]

    def undo_active_count_coords(self, event):
        if button_bool["gt_polyline"] and len(active_countings[0].All_Coordinates) > 0:
            # only do for polygon points
            active_count = objectstorage.active_countings[
                objectstorage.active_countings_index
            ]
            del active_count.All_Coordinates[-1]

            manipulate_image(objectstorage.videoobject.np_image.copy())


class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(fill="x")

        objectstorage.maincanvas = OtcCanvas(
            master=self.frame_canvas, width=0, height=0
        )
        objectstorage.maincanvas.pack()
