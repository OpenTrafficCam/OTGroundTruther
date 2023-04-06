import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path

from PIL import Image, ImageTk

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.config import vehicle_picture_graph
from helpers.filehelper.datamanagement import info_message
from helpers.image_alteration import manipulate_image
from helpers.section import dump_to_flowdictionary
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

        # Add Line-Section
        self.button_line = tk.Button(
            master=self.frame_control_section,
            width=12,
            bg="red",
            text="Add Line",
        )
        self.button_line.grid(row=0, column=0, padx=(10, 10))

        # Add delete-Section
        self.button_line_delete = tk.Button(
            master=self.frame_control_section,
            width=12,
            text="Delete Line",
            command=lambda: self.delete_section(),
        )
        self.button_line_delete.grid(row=0, column=1, padx=(10, 10))

    def display_chosen_vhv_class(self, event):
        picture_path = vehicle_picture_graph[event.keysym]
        image1 = Image.open(Path("assets", picture_path))
        img = image1.resize((80, 80))
        self.test = ImageTk.PhotoImage(img)
        self.control_label1.configure(image=self.test)

    def button_line_switch(self, opposite_button):
        objectstorage.config_dict[
            "linedetector_toggle"
        ] = not objectstorage.config_dict["linedetector_toggle"]
        objectstorage.config_dict["gt_active"] = not objectstorage.config_dict[
            "gt_active"
        ]
        print(
            "Drawing Section:" + str(objectstorage.config_dict["linedetector_toggle"])
        )
        if objectstorage.config_dict["linedetector_toggle"]:
            self.button_line.configure(bg="green")
            opposite_button.configure(bg="red")

        else:
            self.button_line.configure(bg="red")
            opposite_button.configure(bg="green")

    def add_section(self, entrywidget):
        """Saves created section to flowfile.

        Args:
            maincanvas (tkinter.canvas): needed to hand over canvas coordinates.
            flow_dict (dictionary): Dictionary with view.sections and movements.
            entrywidget (tkinter.widget): Entrywidget to put in sectionname.
        """

        detector_name = entrywidget.get()

        if detector_name in objectstorage.flow_dict["Detectors"].keys():
            tk.messagebox.showinfo(
                title="Warning", message="Sectionname already exists!"
            )

        else:

            dump_to_flowdictionary(detector_name)

            self.tree_sections.insert(parent="", index="end", text=detector_name)

            self.on_close(),

    def delete_section(self):

        itemlist = list(self.tree_sections.selection())

        if not itemlist:
            info_message("Warning", "Please select detector you wish to delete!")

            return

        for sectionitem in itemlist:

            detector_name = self.tree_sections.item(sectionitem, "text")

            self.tree_sections.delete(sectionitem)

            del objectstorage.flow_dict["Detectors"][detector_name]

            manipulate_image(objectstorage.videoobject.np_image.copy())

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

    def create_section_entry_window(self):
        """Creates toplevel window to name view.sections."""

        # only if line or polygon creation is activate
        if (
            objectstorage.config_dict["linedetector_toggle"]
            or objectstorage.config_dict["polygondetector_toggle"]
        ):

            self.new_detector_creation = tk.Toplevel()
            self.new_detector_creation.geometry("%dx%d+%d+%d" % (250, 50, 850, 350))

            # removes hotkey so "enter" won't trigger
            config.RETURN_KEYBIND_IS_ENABLED = False

            detector_name_entry = tk.Entry(master=self.new_detector_creation)

            detector_name_entry.grid(row=1, column=0, sticky="w", pady=10, padx=10)
            detector_name_entry.focus()

            safe_section = tk.Button(
                master=self.new_detector_creation,
                text="Add section",
                command=lambda: [
                    self.add_section(detector_name_entry),
                ],
            )

            safe_section.grid(row=1, column=1, sticky="w", pady=10, padx=10)
            self.new_detector_creation.protocol("WM_DELETE_WINDOW", self.on_close)
            # makes the background window unavailable
            self.new_detector_creation.grab_set()

    def on_close(self):
        # hotkeys
        config.RETURN_KEYBIND_IS_ENABLED = True
        self.new_detector_creation.destroy()

        manipulate_image(objectstorage.videoobject.np_image.copy())
