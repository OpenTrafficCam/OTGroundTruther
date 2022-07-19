from helpers.canvas import CanvasFrame
import tkinter as tk
from helpers.video import load_video_and_frame
import helpers.objectstorage as objectstorage
from helpers.image_alteration import manipulate_image
from helpers.view_activecount import FrameActiveCounts
from helpers.view_gt import FrameGT
from helpers.count import initialize_new_count
from helpers.count_manipulation import assign_vehicle_class
from helpers.datamanagement import fill_background_dic, fill_ground_truth
from helpers.view_section import FrameSection
import keyboard


class gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTGT")
        self.set_layout()

        # hotkeys
        keyboard.add_hotkey(
            "enter", lambda: self.frame_sections.create_section_entry_window()
        )

        self.add_canvas_frame()
        self.bind("<MouseWheel>", self.mouse_scroll)
        self.bind("<Right>", self.arrow_key_scroll)
        self.bind("<Left>", self.arrow_key_scroll)
        self.bind("+", self.change_scroll_up)
        self.bind("-", self.change_scroll_down)
        self.bind("n", initialize_new_count, add="+")
        self.bind(
            "n", self.frame_active_counts.insert_active_count_to_treeview, add="+"
        )
        self.bind("c", assign_vehicle_class, add="+")
        self.bind("c", self.frame_active_counts.update_treeview, add="+")
        self.bind("<Return>", self.frame_active_counts.delete_from_treeview, add="+")
        self.bind("<Return>", self.frame_gt.insert_to_gt_treeview, add="+")
        self.bind("<Return>", fill_background_dic, add="+")
        self.bind("<Return>", fill_ground_truth, add="+")

        # bind functions to canvas // prevent circular import
        objectstorage.maincanvas.bind(
            "<ButtonPress-1>",
            lambda event: [
                objectstorage.maincanvas.click_receive_vehicle_coordinates(event),
                objectstorage.maincanvas.click_receive_section_coordinates(event, 0),
                self.frame_active_counts.update_treeview(event),
            ],
        )

    def change_scroll_up(self, event):
        print("scrollspeed:" + str(objectstorage.videoobject.scroll_speed))
        if objectstorage.videoobject.scroll_speed < 5:
            objectstorage.videoobject.scroll_speed += 1

    def change_scroll_down(self, event):
        print("scrollspeed:" + str(objectstorage.videoobject.scroll_speed))
        if objectstorage.videoobject.scroll_speed > 1:
            objectstorage.videoobject.scroll_speed -= 1

    def mouse_scroll(self, event):

        if event.delta > 1:
            objectstorage.videoobject.current_frame += (
                1 * objectstorage.videoobject.scroll_speed
            )

        else:
            objectstorage.videoobject.current_frame -= (
                1 * objectstorage.videoobject.scroll_speed
            )

        objectstorage.videoobject.set_frame()

        manipulate_image(objectstorage.videoobject.np_image.copy())

    def arrow_key_scroll(self, event):

        if event.keycode == 39:
            objectstorage.videoobject.current_frame += (
                1 * objectstorage.videoobject.scroll_speed
            )

        else:
            objectstorage.videoobject.current_frame -= (
                1 * objectstorage.videoobject.scroll_speed
            )

        objectstorage.videoobject.set_frame()
        manipulate_image(objectstorage.videoobject.np_image.copy())

    def set_layout(
        self,
    ):
        frame_canvas = tk.Frame(master=self)
        frame_canvas.pack()

        frame_controlpanel = tk.Frame(master=self)
        frame_controlpanel.pack(fill="x")

        # creates CanvasFrame with OTCanvas Class in it
        canvas = CanvasFrame(master=frame_canvas)
        canvas.pack()

        # Frame for creating GT file
        self.frame_active_counts = FrameActiveCounts(master=frame_controlpanel)
        self.frame_active_counts.pack(side="left", fill="both")

        self.frame_gt = FrameGT(master=frame_controlpanel)
        self.frame_gt.pack(side="left", fill="both")

        # Frame for section creation
        self.frame_sections = FrameSection(master=frame_controlpanel)
        self.frame_sections.pack(side="top", fill="x")

        objectstorage.videoobject = load_video_and_frame()

    def add_canvas_frame(self):
        np_image = objectstorage.videoobject.get_frame(np_image=True)

        objectstorage.maincanvas.configure(
            width=objectstorage.videoobject.width,
            height=objectstorage.videoobject.height,
        )
        manipulate_image(np_image)


def main():
    """Main function."""
    app = gui()
    app.resizable(False, False)

    app.mainloop()
