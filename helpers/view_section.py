import tkinter.ttk as ttk
import tkinter as tk
from helpers.image_alteration import manipulate_image
import helpers.objectstorage as objectstorage
import keyboard
from helpers.section import button_line_switch, dump_to_flowdictionary


class FrameSection(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Section", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(fill="x")

        # Files treeview
        self.tree_sections = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_sections.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        self.tree_sections.bind(
            "<<TreeviewSelect>>",  # self.tree_detector_selection
        )

        tree_files_cols = {
            "#0": "Section",
        }
        self.tree_sections["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_sections.column("#0", anchor="center")
        self.tree_sections.heading("#0", text=tree_files_cols["#0"], anchor="center")

        self.frame_control_section = tk.Frame(master=self)
        self.frame_control_section.pack()

        # Add Line-Section
        self.button_line = tk.Button(
            master=self.frame_control_section,
            width=12,
            text="Add Line",
            command=lambda: button_line_switch(),
        )
        self.button_line.grid(row=0, column=0, padx=(10, 0))

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

            # TODO: #67 Prevent duplicate section names
            dump_to_flowdictionary(detector_name)

            self.tree_sections.insert(parent="", index="end", text=detector_name)

            self.on_close(),

    def create_section_entry_window(self):
        """Creates toplevel window to name view.sections."""

        # only if line or polygon creation is activate
        if (
            objectstorage.button_bool["linedetector_toggle"]
            or objectstorage.button_bool["polygondetector_toggle"]
        ):

            self.new_detector_creation = tk.Toplevel()
            self.new_detector_creation.geometry("%dx%d+%d+%d" % (250, 50, 850, 350))

            # removes hotkey so "enter" won't trigger
            keyboard.remove_hotkey("enter")

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
        keyboard.add_hotkey(
            "enter",
            lambda: self.create_section_entry_window(),
        )
        self.new_detector_creation.destroy()

        objectstorage.maincanvas.delete_points()

        manipulate_image(objectstorage.videoobject.np_image.copy())