import tkinter as tk

import helpers.filehelper.objectstorage as objectstorage
import view.config as config
from helpers.count.count import initialize_new_count
from helpers.count.count_manipulation import assign_vehicle_class
from helpers.filehelper.config import vehicle_definition
from helpers.filehelper.datamanagement import (
    fill_eventbased_dictionary,
    fill_ground_truth,
    load_event_dic_from_csv,
    load_flowfile,
    quick_safe_to_csv,
    reset_active_count,
    safe_eventbased_dataframe,
    save_flowfile,
)
from helpers.image_alteration import manipulate_image
from helpers.section import shapely_object
from helpers.video import load_video_and_frame
from view.canvas import CanvasFrame
from view.view_activecount import FrameActiveCounts
from view.view_gt import FrameGT
from view.view_section import FrameSection


def handle_left_arrow_key_event(_):
    rewind_video()


def handle_right_arrow_key_event(_):
    forward_video()


def forward_video() -> None:
    objectstorage.videoobject.current_frame += (
        1 * objectstorage.videoobject.scroll_speed
    )
    objectstorage.videoobject.set_frame()
    manipulate_image(objectstorage.videoobject.np_image.copy())


def rewind_video() -> None:
    objectstorage.videoobject.current_frame -= (
        1 * objectstorage.videoobject.scroll_speed
    )
    objectstorage.videoobject.set_frame()
    manipulate_image(objectstorage.videoobject.np_image.copy())


class gui(tk.Tk):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title("OTGT")
        self.set_layout()

        # hotkeys
        config.RETURN_KEYBIND_IS_ENABLED = True

        if objectstorage.use_test_version is not None:
            self.add_canvas_frame()

        self._init_mouse_scroll_keybind()

        self.bind(config.MIDDLE_CLICK_EVENT, self.undo_active_count_coords)
        self.bind("<Right>", handle_right_arrow_key_event)
        self.bind("<Left>", handle_left_arrow_key_event)
        self.bind("+", self.change_scroll_up)
        self.bind("-", self.change_scroll_down)

        self.bind("<Up>", self.change_active_countings_index, add="+")
        self.bind("<Down>", self.change_active_countings_index, add="+")
        self.bind("<Up>", self.frame_active_counts.update_treeview, add="+")
        self.bind("<Down>", self.frame_active_counts.update_treeview, add="+")

        # temporary deactivated
        # self.bind("m", self.jump_to_frame)

        for i in vehicle_definition.keys():
            self.bind(str(i), self._vehicle_call_key_pressed)

        self.bind("<Return>", self.handle_right_click_event)


        self.bind("<Escape>", self.cancel_active_count)

        self.bind("<F5>", quick_safe_to_csv)

        # bind functions to canvas // prevent circular import
        objectstorage.maincanvas.bind(
            config.LEFT_CLICK_EVENT, self.handle_left_click_event
        )
        objectstorage.maincanvas.bind(
            config.RIGHT_CLICK_EVENT, self.handle_right_click_event
        )
    def _vehicle_call_key_pressed(self, event):
        assign_vehicle_class(event)
        self.frame_sections.display_chosen_vhv_class(event)
        self.frame_active_counts.update_treeview(event)
        objectstorage.maincanvas.update_image()

    def _init_mouse_scroll_keybind(self):
        def windows_handler(event):
            if event.delta > 0:
                forward_video()
            else:
                rewind_video()

        def macos_handler(event):
            if event.delta > 0:
                rewind_video()
            else:
                forward_video()

        if config.ON_MAC:
            self.bind("<MouseWheel>", macos_handler)
        elif config.ON_WINDOWS:
            self.bind("<MouseWheel>", windows_handler)
        else:
            self.bind("<Button-5>", lambda _: forward_video())  # scroll up
            self.bind("<Button-4>", lambda _: rewind_video())  # scroll down

    def handle_return_pressed_event(self, _):
        if config.RETURN_KEYBIND_IS_ENABLED:
            self.frame_sections.create_section_entry_window()

    def handle_left_click_event(self, event):
        initialize_new_count(event)
        self.frame_active_counts.insert_active_count_to_treeview(event)
        objectstorage.maincanvas.click_receive_vehicle_coordinates(event)
        objectstorage.maincanvas.click_receive_section_coordinates(event, 0)
        self.frame_active_counts.update_treeview(event)

    # for finish the actual count
    def handle_right_click_event(self, event):
        self.frame_sections.create_section_entry_window()

        self.frame_active_counts.delete_from_treeview(event=event, reset=False)
        self.frame_gt.insert_to_gt_treeview(event=event)
        fill_eventbased_dictionary(event=event)
        fill_ground_truth(event=event)
        self.frame_sections.reset_shown_vhv_class()
        self.reset_index(event=event)
        objectstorage.maincanvas.update_image()

    def cancel_active_count(self, event):
        self.frame_active_counts.delete_from_treeview(event=event, reset=True)
        self.frame_sections.reset_shown_vhv_class()
        reset_active_count()
        self.reset_index(event=event)
        objectstorage.maincanvas.update_image()

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
        if objectstorage.videoobject.scroll_speed < 100:
            objectstorage.videoobject.scroll_speed += 1

    def change_scroll_down(self, event):
        print("scrollspeed:" + str(objectstorage.videoobject.scroll_speed))
        if objectstorage.videoobject.scroll_speed > 1:
            objectstorage.videoobject.scroll_speed -= 1

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

        self.frame_active_counts.button_count.configure(
            command=lambda: self.frame_active_counts.button_count_switch(
                self.frame_sections.button_line
            )
        )
        self.frame_sections.button_line.configure(
            command=lambda: self.frame_sections.button_line_switch(
                self.frame_active_counts.button_count
            )
        )

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

    def import_flowfile(self):  # new function for importing
        """Calls load_flowfile-function and inserts view.sections to listboxwidget."""
        objectstorage.flow_dict = load_flowfile()

        # create a new list of dictionaries ro insert imported section
        # better workaround ==> get dic by key value pair(i.g. section id) with listcomprehension and change value
        # [d for d in dictionaries if d.get(key) == value]
        imported_sections = []

        for detector in objectstorage.flow_dict["sections"]:
            print(detector)
            print("----------------")
            x1 = int(
                detector["coordinates"][0]["x"] * objectstorage.videoobject.x_resize_factor)
            y1 = int(
                detector["coordinates"][0]["y"] * objectstorage.videoobject.y_resize_factor)
            x2 = int(
                detector["coordinates"][1]["x"] * objectstorage.videoobject.x_resize_factor)
            y2 = int(
                detector["coordinates"][1]["y"] * objectstorage.videoobject.y_resize_factor)

            imported_sections.append({"id": detector["id"], "type": "line",
                                      "relative_offset_coordinates": {"section-enter": {"x": 0.5, "y": 0.5}},
                                      "coordinates": [{"x": x1, "y": y1}, {"x": x2, "y": y2}], "plugin_data": {}, "Geometry_line": shapely_object(x1, y1, x2, y2, linestring=True)})

            self.frame_sections.tree_sections.insert(
                parent="", index="end", text=detector["id"]
            )
        objectstorage.flow_dict["sections"] = imported_sections
        print("finished")

        manipulate_image(objectstorage.videoobject.np_image.copy())

    # def import_flowfile(self):
    #     """Calls load_flowfile-function and inserts view.sections to listboxwidget."""
    #     objectstorage.flow_dict = load_flowfile()
    #     print(objectstorage.flow_dict)

    #     for detector in objectstorage.flow_dict["Detectors"]:

    #         x1 = int(objectstorage.flow_dict["Detectors"][detector]
    #                  ["start_x"] * objectstorage.videoobject.x_resize_factor)
    #         y1 = int(objectstorage.flow_dict["Detectors"][detector]
    #                  ["start_y"] * objectstorage.videoobject.y_resize_factor)
    #         x2 = int(objectstorage.flow_dict["Detectors"][detector]
    #                  ["end_x"] * objectstorage.videoobject.x_resize_factor)
    #         y2 = int(objectstorage.flow_dict["Detectors"][detector]
    #                  ["end_y"] * objectstorage.videoobject.y_resize_factor)

    #         objectstorage.flow_dict["Detectors"][detector]["start_x"] = x1
    #         objectstorage.flow_dict["Detectors"][detector]["start_y"] = y1
    #         objectstorage.flow_dict["Detectors"][detector]["end_x"] = x2
    #         objectstorage.flow_dict["Detectors"][detector]["end_y"] = y2

    #         # when imported calculates the shapelyobjects fron detector coords
    #         objectstorage.flow_dict["Detectors"][detector][
    #             "Geometry_line"
    #         ] = shapely_object(x1, y1, x2, y2, linestring=True)

    #         self.frame_sections.tree_sections.insert(
    #             parent="", index="end", text=detector
    #         )

    #     manipulate_image(objectstorage.videoobject.np_image.copy())

    def undo_active_count_coords(self, event):
        if not objectstorage.active_countings:
            return
        if (
            len(
                objectstorage.active_countings[
                    objectstorage.active_countings_index
                ].Coordinates
            )
            > 1
        ):
            active_count = objectstorage.active_countings[
                objectstorage.active_countings_index
            ]
            del active_count.Coordinates[-1]
            del active_count.Frames[-1]
            del active_count.Gates[-1]

            print("Last rightclick deleted")

            manipulate_image(objectstorage.videoobject.np_image.copy())


def main():  # sourcery skip: remove-redundant-if
    """Main function."""
    # use_test_version = input("Type y to use testversion? \n")

    # if str(use_test_version) != "y":
    #     use_test_version = None
    # # else:
    # #     use_test_version = None

    # objectstorage.use_test_version = use_test_version
    objectstorage.use_test_version = None

    app = gui()
    # app.resizable(False, False)

    menubar = tk.Menu(app)
    file = tk.Menu(
        menubar,
        tearoff=0,
    )
    file.add_command(
        label="Import videofile",
        command=lambda: [load_video_and_frame(), app.add_canvas_frame()],
    )
    file.add_separator()
    file.add_command(label="Import flowfile", command=app.import_flowfile)
    file.add_command(label="Save flowfile", command=save_flowfile)

    file.add_separator()
    file.add_command(label="Save events", command=safe_eventbased_dataframe)
    file.add_command(
        label="Load events",
        command=lambda: [
            load_event_dic_from_csv(
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
