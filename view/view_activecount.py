import tkinter as tk
import tkinter.ttk as ttk
import helpers.objectstorage as objectstorage


class FrameActiveCounts(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Active counts", **kwargs)
        self.frame_active_counts = tk.Frame(master=self)
        self.frame_active_counts.pack(
            fill="x",
        )

        # Files treeview
        self.tree_active_countings = ttk.Treeview(
            master=self.frame_active_counts, height=3
        )
        self.tree_active_countings.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        tree_files_cols = {
            "#0": "ID",
            "Class": "Class",
            "Crossed Gates": "Crossed Gates",
        }
        self.tree_active_countings["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_active_countings.column("#0", anchor="center", width=50)
        self.tree_active_countings.heading(
            "#0", text=tree_files_cols["#0"], anchor="center"
        )
        self.tree_active_countings.column("Class", anchor="center", width=50)
        self.tree_active_countings.heading(
            "Class", text=tree_files_cols["Class"], anchor="center"
        )

        self.tree_active_countings.column("Crossed Gates", anchor="center", width=50)
        self.tree_active_countings.heading(
            "Crossed Gates", text=tree_files_cols["Crossed Gates"], anchor="center"
        )

        self.frame_control_active_counts = tk.Frame(master=self)
        self.frame_control_active_counts.pack()

        self.button_count_line = tk.Button(
            master=self.frame_control_active_counts,
            width=12,
            text="Activate Counting",
            command=lambda: self.button_count_type_line_switch(),
        )
        self.button_count_line.grid(row=0, column=1, padx=(10, 0))

    def insert_active_count_to_treeview(self, event):
        # insert latest item from activecount list
        # if button n is pressed or there is no active count
        if event.keysym_num == 110 or not objectstorage.config_dict["count_active"]:

            objectstorage.config_dict["count_active"] = True
            latest_count = objectstorage.active_countings[-1]

            self.tree_active_countings.insert(
                "",
                tk.END,
                text=latest_count.ID,
                values=(
                    latest_count.Vhc_class,
                    "None",
                ),
            )
            self.update_treeview(self)

    def update_treeview(self, event):
        # make selectable
        if not objectstorage.active_countings:
            return
        count_ID = objectstorage.active_countings[
            objectstorage.active_countings_index
        ].ID

        count = objectstorage.active_countings[objectstorage.active_countings_index]

        children = self.tree_active_countings.get_children("")
        for child in children:
            values = self.tree_active_countings.item(child, "text")

            if int(count_ID) == int(values):
                
                self.tree_active_countings.item(
                    child,
                    values=(
                        count.Vhc_class,
                        ["None" if count.Gates == [] else count.Gates],
                    ),
                )
        # could be anywhere in code
        # objectstorage.active_countings[
        #     objectstorage.active_countings_index
        # ].get_intersect_and_frame(self)

        # highlights and selectes treeview item
        iid = self.tree_active_countings.get_children()[
            objectstorage.active_countings_index
        ]
        self.tree_active_countings.selection_set(iid)

    def delete_from_treeview(self, event):
        # make selectable
        if (
            objectstorage.active_countings
            and objectstorage.active_countings[
                objectstorage.active_countings_index
            ].all_values_set()
        ):
            count_ID = objectstorage.active_countings[
                objectstorage.active_countings_index
            ].ID

            children = self.tree_active_countings.get_children("")
            for child in children:
                values = self.tree_active_countings.item(child, "text")
                if int(count_ID) == int(values):
                    self.tree_active_countings.delete(child)

    def button_count_type_line_switch(self):

        objectstorage.config_dict["gt_active"] = not objectstorage.config_dict[
            "gt_active"
        ]
        print(objectstorage.config_dict["gt_active"])
