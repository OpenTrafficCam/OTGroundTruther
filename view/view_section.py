import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

from PIL import Image, ImageTk

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.config import vehicle_picture_graph
from helpers.image_alteration import manipulate_image
from view import config


class FrameSection(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Section", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="y")

        # Files treeview
        self.tree_sections = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_sections.pack(
            anchor=tk.W,
            padx=10,
            pady=10,
        )

        image1 = Image.open(Path("assets", "placeholder.png"))
        img = image1.resize((80, 80))
        self.test = ImageTk.PhotoImage(img)

        self.control_label1 = tk.Label(master=self.frame_tree, image=self.test)

        self.control_label1.config(bg="white")

        self.tree_sections.pack(
            in_=self.frame_tree,
            side=tk.LEFT,
            padx=5,
            pady=10,
        )
        self.control_label1.pack(
            in_=self.frame_tree,
            side=tk.RIGHT,
            padx=5,
            pady=10,
        )

        # TODO #11 cant prevent arrows from browsing through section treeview

        self.tree_sections.bind(
            "<<TreeviewSelect>>",
        )
        # self.tree_detector_selection

        tree_files_cols = {
            "#0": "Section",
        }
        self.tree_sections["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_sections.column("#0", anchor="center", width=100)
        self.tree_sections.heading("#0", text=tree_files_cols["#0"], anchor="center")

        self.frame_control_section = tk.Frame(master=self)
        self.frame_control_section.pack()

    def display_chosen_vhv_class(self, event):
        self.display_class_image(event.keysym)

    def reset_shown_vhv_class(self):
        self.display_class_image("reset")

    def display_class_image(self, key):
        picture_path = vehicle_picture_graph[key]
        image1 = Image.open(Path("assets", picture_path))
        img = image1.resize((80, 80))
        self.test = ImageTk.PhotoImage(img)
        self.control_label1.configure(image=self.test)

    def tree_section_selection(self, event):
        """Re draws detectors, where the selected detectors has different color

        Args:
            event (tkinter.event): Section selection from  listbox.
        """

        selectionlist_sections = []

        for item in self.tree_sections.selection():
            detector_name = self.tree_sections.item(item, "text")
            selectionlist_sections.append(detector_name)

        for dict_key in objectstorage.flow_dict["Detectors"].keys():

            if dict_key in selectionlist_sections:

                objectstorage.flow_dict["Detectors"][dict_key]["color"] = (
                    200,
                    0,
                    0,
                    255,
                )

            else:
                objectstorage.flow_dict["Detectors"][dict_key]["color"] = (
                    200,
                    125,
                    125,
                    255,
                )

        manipulate_image(objectstorage.videoobject.np_image.copy())

    def on_close(self):
        # hotkeys
        config.RETURN_KEYBIND_IS_ENABLED = True
        self.new_detector_creation.destroy()

        manipulate_image(objectstorage.videoobject.np_image.copy())
