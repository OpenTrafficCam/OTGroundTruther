import tkinter as tk
import helpers.objectstorage as objectstorage
from helpers.objectstorage import active_countings, button_bool
from helpers.count import current_count
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
            "<ButtonPress-1>",
            lambda event: [
                self.click_receive_vehicle_coordinates(event),
                self.click_receive_section_coordinates(event, 0),
            ],
        )

        self.bind(
            "<B1-Motion>",
            lambda event: [
                self.click_receive_section_coordinates(event, 1),
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
        # uses mouseevents to get coordinates (left button)
        self.coordinateX = int(self.canvasx(event.x))
        self.coordinateY = int(self.canvasy(event.y))

        if not active_countings:
            # create instance if no counting object is active
            active_countings.append(current_count())

        if not active_countings[0].first_coordinate:

            active_countings[0].Entry_Coordinate = (
                self.coordinateX,
                self.coordinateY,
            )
            active_countings[0].Entry_Frame = objectstorage.videoobject.current_frame
            active_countings[0].first_coordinate = True
        else:
            active_countings[0].Exit_Coordinate = (
                self.coordinateX,
                self.coordinateY,
            )
            active_countings[0].Exit_Frame = objectstorage.videoobject.current_frame
            active_countings[0].first_coordinate = False
        active_countings[0].line_drawn = not active_countings[0].first_coordinate
        manipulate_image(objectstorage.videoobject.np_image.copy())

    def delete_points(self):
        """delete list of polygon points after scrolling, sliding, playing, rewinding"""
        if self.polygon_points:
            self.polygon_points = []
        else:
            self.points = [(0, 0), (0, 0)]


class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(fill="x")

        objectstorage.maincanvas = OtcCanvas(
            master=self.frame_canvas, width=0, height=0
        )
        objectstorage.maincanvas.pack()
