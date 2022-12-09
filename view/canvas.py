import tkinter as tk
from tkinter import messagebox
import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.objectstorage import config_dict

from helpers.image_alteration import manipulate_image
from math import atan2, dist
import numpy as np


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


    def click_receive_section_coordinates(self, event, list_index):
        """Saves coordinates from canvas event to linepoint list.

        Args:
            event (tkinter.event): Click on canvas triggers event.
            list_index (index): 0 : start, 1 : end
        """
        if config_dict["linedetector_toggle"]:
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
        if config_dict["linedetector_toggle"]:
            return
        # if not objectstorage.active_countings:
        #     messagebox.showinfo(
        #         title="Info",
        #         message="First create empty count with hotkey n",
        #     )
        #     return
        if config_dict["gt_active"]:

            self.coordinateX = int(self.canvasx(event.x))
            self.coordinateY = int(self.canvasy(event.y))

        self.assign_information(event)
             
        manipulate_image(objectstorage.videoobject.np_image.copy())

    def assign_information(self,event):
        """depending on left or right mousclick and if click is in section
           coorindates get added, reseted or initilized
        """
        for gate in objectstorage.flow_dict["Detectors"]:
            p0 = (objectstorage.flow_dict["Detectors"][gate]['start_x'],objectstorage.flow_dict["Detectors"][gate]['start_y'])
            p1 = (objectstorage.flow_dict["Detectors"][gate]['end_x'],objectstorage.flow_dict["Detectors"][gate]['end_y'])
            middle_point_x = (p0[0] + p1[0]) / 2
            middle_point_y = (p0[1] + p1[1]) / 2
            x = self.coordinateX - middle_point_x
            # mirror the y-values because the y-axis in the frame is mirrored 
            y = - self.coordinateY + middle_point_y
            radian = atan2(p1[1] - p0[1],p0[0] - p1[0])


            a = dist(p0, p1) / 2
            b = a * 0.15
            # turned ellipse equation

            if (x * np.cos(radian) + y * np.sin(radian)) ** 2 / a ** 2 + (x * np.sin(radian) - y * np.cos(radian)) ** 2 / b ** 2 <= 1:

                print(f"Coordinate in the gate: {gate}")

                if event.num == 3 and bool(objectstorage.active_countings[objectstorage.active_countings_index].Gates and objectstorage.active_countings[objectstorage.active_countings_index].Gates[-1] != gate ):
                    # append on right click
                    objectstorage.active_countings[objectstorage.active_countings_index].Gates.append(gate)
                    objectstorage.active_countings[objectstorage.active_countings_index].Coordinates.append((self.coordinateX,self.coordinateY))
                    objectstorage.active_countings[objectstorage.active_countings_index].Frames.append(objectstorage.videoobject.current_frame)
                    
                    break
                elif event.num == 3 and bool(objectstorage.active_countings[objectstorage.active_countings_index].Gates and objectstorage.active_countings[objectstorage.active_countings_index].Gates[-1] == gate ):
                    #create on left click
                    objectstorage.active_countings[objectstorage.active_countings_index].Coordinates[-1] = (self.coordinateX,self.coordinateY,)
                    objectstorage.active_countings[objectstorage.active_countings_index].Frames[-1] = objectstorage.videoobject.current_frame
                elif event.num == 1:
                    objectstorage.active_countings[objectstorage.active_countings_index].Gates = [gate]
                    objectstorage.active_countings[objectstorage.active_countings_index].Coordinates = [(self.coordinateX,self.coordinateY,)]
                    objectstorage.active_countings[objectstorage.active_countings_index].Frames = [objectstorage.videoobject.current_frame]
                    break
            # delete if not clicked in section
            elif event.num == 1:
                    objectstorage.active_countings[objectstorage.active_countings_index].Gates = []
                    objectstorage.active_countings[objectstorage.active_countings_index].Coordinates = []
                    objectstorage.active_countings[objectstorage.active_countings_index].Frames = []



class CanvasFrame(tk.Frame):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.frame_canvas = tk.Frame(master=self)
        self.frame_canvas.pack(fill="x")

        objectstorage.maincanvas = OtcCanvas(
            master=self.frame_canvas, width=0, height=0
        )
        objectstorage.maincanvas.pack()
