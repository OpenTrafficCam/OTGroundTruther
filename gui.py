from helpers.canvas import CanvasFrame
import tkinter as tk
from helpers.video import load_video_and_frame
import helpers.objectstorage as objectstorage
from helpers.image_alteration import manipulate_image
from helpers.view_activecount import FrameActiveCounts
from helpers.count import assign_vehicle_class, initialize_new_count, fill_ground_truth
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
        self.bind("+", self.change_scroll_up)
        self.bind("-", self.change_scroll_down)
        self.bind("n", initialize_new_count)
        self.bind("c", assign_vehicle_class)
        self.bind("<Return>", fill_ground_truth)

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
        controlpanel = FrameActiveCounts(master=frame_controlpanel)
        controlpanel.pack(side="left", fill="both")

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
