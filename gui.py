from helpers.canvas import CanvasFrame
import tkinter as tk
from helpers.video import load_video_and_frame
import helpers.objectstorage as objectstorage
from helpers.image_alteration import manipulate_image
from helpers.view_activecount import FrameActiveCounts
from helpers.view_gt import FrameGT
from helpers.count import initialize_new_count
from helpers.count_manipulation import assign_vehicle_class
from helpers.datamanagement import (
    fill_background_dic,
    fill_ground_truth,
    load_flowfile,
    save_flowfile,
    safe_gt_to_csv,
    quick_safe_to_csv,
    load_gt_from_csv,
)
from helpers.view_section import FrameSection
import keyboard
from helpers.section import shapely_object


class gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTGT")
        self.set_layout()

        # hotkeys
        keyboard.add_hotkey(
            "enter", lambda: self.frame_sections.create_section_entry_window()
        )
        if objectstorage.use_test_version is not None:
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
        self.bind("<Up>", self.change_active_countings_index, add="+")
        self.bind("<Down>", self.change_active_countings_index, add="+")
        self.bind("<Up>", self.frame_active_counts.update_treeview, add="+")
        self.bind("<Down>", self.frame_active_counts.update_treeview, add="+")

        self.bind("m", self.jump_to_frame)

        self.bind("b", assign_vehicle_class, add="+")
        self.bind("t", assign_vehicle_class, add="+")
        self.bind("c", assign_vehicle_class, add="+")
        self.bind("b", self.frame_active_counts.update_treeview, add="+")
        self.bind("t", self.frame_active_counts.update_treeview, add="+")
        self.bind("c", self.frame_active_counts.update_treeview, add="+")
        self.bind("<Return>", self.frame_active_counts.delete_from_treeview, add="+")
        self.bind("<Return>", self.frame_gt.insert_to_gt_treeview, add="+")
        self.bind("<Return>", fill_background_dic, add="+")
        self.bind("<Return>", fill_ground_truth, add="+")
        self.bind("<Return>", self.reset_index, add="+")
        self.bind("<F5>", quick_safe_to_csv)

        # bind functions to canvas // prevent circular import
        objectstorage.maincanvas.bind(
            "<ButtonPress-1>",
            lambda event: [
                objectstorage.maincanvas.click_receive_vehicle_coordinates(event),
                objectstorage.maincanvas.click_receive_section_coordinates(event, 0),
                self.frame_active_counts.update_treeview(event),
            ],
        )

    def jump_to_frame(self, event):
        if not objectstorage.active_countings:
            return
        objectstorage.videoobject.current_frame = objectstorage.active_countings[
            objectstorage.active_countings_index
        ].Entry_Frame

        objectstorage.videoobject.set_frame()

        manipulate_image(objectstorage.videoobject.np_image.copy())

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

        elif (
            objectstorage.videoobject.current_frame
            - 1 * objectstorage.videoobject.scroll_speed
        ) >= 0:
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

        elif objectstorage.videoobject.current_frame > 0:
            objectstorage.videoobject.current_frame -= (
                1 * objectstorage.videoobject.scroll_speed
            )

        objectstorage.videoobject.set_frame()
        manipulate_image(objectstorage.videoobject.np_image.copy())

    def change_active_countings_index(self, event):

        if event.keycode in [38, 40] and len(objectstorage.active_countings) == 0:
            return
        elif (
            event.keycode == 38
            and len(objectstorage.active_countings) > 1
            and (objectstorage.active_countings_index + 1)
            < len(objectstorage.active_countings)
        ):
            objectstorage.active_countings_index += 1

        elif (
            event.keycode == 40
            and (objectstorage.active_countings_index + 1)
            <= len(objectstorage.active_countings)
            and objectstorage.active_countings_index > 0
        ):
            objectstorage.active_countings_index -= 1

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

        if objectstorage.use_test_version is not None:
            objectstorage.videoobject = load_video_and_frame()

    def add_canvas_frame(self):
        np_image = objectstorage.videoobject.get_frame(np_image=True)

        objectstorage.maincanvas.configure(
            width=objectstorage.videoobject.width,
            height=objectstorage.videoobject.height,
        )
        manipulate_image(np_image)

    def reset_index(self, event):

        objectstorage.active_countings_index = 0

        if objectstorage.active_countings:

            iid = self.frame_active_counts.tree_active_countings.get_children()[
                objectstorage.active_countings_index
            ]
            self.frame_active_counts.tree_active_countings.selection_set(iid)

    def import_flowfile(self):
        """Calls load_flowfile-function and inserts view.sections to listboxwidget."""
        objectstorage.flow_dict = load_flowfile()

        for detector in objectstorage.flow_dict["Detectors"]:
            x1 = objectstorage.flow_dict["Detectors"][detector]["start_x"]
            y1 = objectstorage.flow_dict["Detectors"][detector]["start_y"]
            x2 = objectstorage.flow_dict["Detectors"][detector]["end_x"]
            y2 = objectstorage.flow_dict["Detectors"][detector]["end_y"]

            # when imported calculates the shapelyobjects fron detector coords
            objectstorage.flow_dict["Detectors"][detector][
                "Geometry_line"
            ] = shapely_object(x1, y1, x2, y2, linestring=True)
            objectstorage.flow_dict["Detectors"][detector][
                "Geometry_polygon"
            ] = shapely_object(x1, y1, x2, y2)

            self.frame_sections.tree_sections.insert(
                parent="", index="end", text=detector
            )

        manipulate_image(objectstorage.videoobject.np_image.copy())


def main():  # sourcery skip: remove-redundant-if
    """Main function."""
    use_test_version = input("Type y to use testversion? \n")

    if str(use_test_version) != "y":
        use_test_version = None
    # else:
    #     use_test_version = None

    objectstorage.use_test_version = use_test_version

    app = gui()
    # app.resizable(False, False)

    menubar = tk.Menu(app)
    file = tk.Menu(
        menubar,
        tearoff=1,
    )
    file.add_command(label="Import flowfile", command=app.import_flowfile)
    file.add_command(label="Save configuration", command=save_flowfile)
    file.add_command(
        label="Import videofile",
        command=lambda: [load_video_and_frame(), app.add_canvas_frame()],
    )
    file.add_separator()
    file.add_command(label="Save groundtruth", command=safe_gt_to_csv)
    file.add_command(
        label="Load groundtruth",
        command=lambda: [
            load_gt_from_csv(
                app.frame_gt.tree_gt, app.frame_active_counts.tree_active_countings
            ),
            app.frame_gt.fill_treeview(),
        ],
    )
    file.add_separator()
    file.add_command(label="Exit", command=app.quit)
    menubar.add_cascade(label="File", menu=file)
    app.config(menu=menubar)
    app.mainloop()