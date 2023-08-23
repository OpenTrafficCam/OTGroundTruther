import tkinter as tk
import tkinter.ttk as ttk

import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.datamanagement import info_message
from helpers.image_alteration import manipulate_image


class FrameGT(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Ground Truth", **kwargs)
        self.frame_tree = tk.Frame(master=self)
        self.frame_tree.pack(
            fill="x",
        )

        # Files treeview
        self.tree_gt = ttk.Treeview(master=self.frame_tree, height=3)
        self.tree_gt.pack(
            fill="x",
            padx=10,
            pady=10,
        )
        self.frame_control_gt = tk.Frame(master=self)
        self.frame_control_gt.pack()
        # Delete GT-Object
        self.button_line = tk.Button(
            master=self.frame_control_gt,
            width=12,
            text="Delete Object",
            command=lambda: self.delete_from_gt_treeview(),
        )
        self.button_line.grid(row=0, column=0, padx=(10, 10))

        self.tree_gt.bind("<Button-1>", self.click_tree_jump_to_frame)

        tree_files_cols = {
            "#0": "ID",
            "Class": "Class",
        }

        self.tree_gt["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_gt.column("#0", anchor="center", width=10)
        self.tree_gt.heading("#0", text=tree_files_cols["#0"], anchor="center")
        self.tree_gt.column("Class", anchor="center", width=50)
        self.tree_gt.heading("Class", text=tree_files_cols["Class"], anchor="center")

    def insert_to_gt_treeview(self, event):

        if (
            objectstorage.active_countings
            and objectstorage.active_countings[
                objectstorage.active_countings_index
            ].all_values_set()
        ):

            active_count = objectstorage.active_countings[
                objectstorage.active_countings_index
            ]
            self.tree_gt.insert(
                "",
                tk.END,
                text=active_count.ID,
                values=(active_count.Vhc_class,),
            )
            # if count is finished ==> active count object gets deleted
            # maybe need index later

    def click_tree_jump_to_frame(self, event):
        # sourcery skip: do-not-use-bare-except
        curItem = self.tree_gt.focus()
        selected_object_id = self.tree_gt.item(curItem)["text"]

        count = objectstorage.ground_truth[
            objectstorage.ground_truth["ID"] == selected_object_id
        ]

        try:
            selected_frame = count["Crossed_Frames"].str[0]

            objectstorage.videoobject.current_frame = int(selected_frame)

            objectstorage.videoobject.set_frame()

            manipulate_image(objectstorage.videoobject.np_image.copy())
        except Exception:
            return

    def fill_treeview(self):
        for index, row in objectstorage.ground_truth.iterrows():
            self.tree_gt.insert(
                "",
                index,
                text=row["ID"],
                values=row["Class"],
            )

    def delete_from_gt_treeview(self):

        itemlist = list(self.tree_gt.selection())

        if not itemlist:
            info_message("Warning", "Please select GT-item you wish to delete!")

            return

        for grount_truth_object in itemlist:

            object_id = self.tree_gt.item(grount_truth_object, "text")

            self.tree_gt.delete(grount_truth_object)

            #           del objectstorage.eventbased_dictionary[object_id]

            for key in objectstorage.eventbased_dictionary.copy():
                if objectstorage.eventbased_dictionary[key]["TrackID"] == object_id:
                    del objectstorage.eventbased_dictionary[key]

            objectstorage.ground_truth = objectstorage.ground_truth[
                objectstorage.ground_truth["ID"] != object_id
            ]

        manipulate_image(objectstorage.videoobject.np_image.copy())
