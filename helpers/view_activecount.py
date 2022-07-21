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
            "Start": "Start",
            "End": "End",
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
        self.tree_active_countings.column("Start", anchor="center", width=50)
        self.tree_active_countings.heading(
            "Start", text=tree_files_cols["Start"], anchor="center"
        )
        self.tree_active_countings.column("End", anchor="center", width=50)
        self.tree_active_countings.heading(
            "End", text=tree_files_cols["End"], anchor="center"
        )
        self.tree_active_countings.column("Crossed Gates", anchor="center", width=50)
        self.tree_active_countings.heading(
            "Crossed Gates", text=tree_files_cols["Crossed Gates"], anchor="center"
        )

        self.frame_control_active_counts = tk.Frame(master=self)
        self.frame_control_active_counts.pack()

        self.button_count_polyline = tk.Button(
            master=self.frame_control_active_counts,
            width=12,
            text="Polyline",
            command=lambda: self.button_count_type_poly_switch(),
        )
        self.button_count_polyline.grid(row=0, column=0, padx=(10, 0))

        self.button_count_line = tk.Button(
            master=self.frame_control_active_counts,
            width=12,
            text="Line",
            command=lambda: self.button_count_type_line_switch(),
        )
        self.button_count_line.grid(row=0, column=1, padx=(10, 0))

    def insert_active_count_to_treeview(self, event):
        # insert latest item from activecount list
        latest_count = objectstorage.active_countings[-1]

        self.tree_active_countings.insert(
            "",
            tk.END,
            text=latest_count.ID,
            values=(
                latest_count.Vhc_class,
                latest_count.Entry_Coordinate,
                latest_count.Exit_Coordinate,
                [
                    "None"
                    if latest_count.Crossed_gates == []
                    else list(zip(*latest_count.Crossed_gates))[0]
                ],
            ),
        )

    def update_treeview(self, event):
        # selected_item = self.tree_active_countings.selection()[0]
        # print(selected_item)
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

            if count_ID == values:

                self.tree_active_countings.item(
                    child,
                    values=(
                        count.Vhc_class,
                        count.Entry_Coordinate,
                        count.Exit_Coordinate,
                        [
                            "None"
                            if count.Crossed_gates == []
                            else list(zip(*count.Crossed_gates))[0]
                        ],
                    ),
                )
        objectstorage.active_countings[
            objectstorage.active_countings_index
        ].intersection_list(self)

        # highlights and selectes treeview item
        print(objectstorage.active_countings_index)
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
                if count_ID == values:
                    self.tree_active_countings.delete(child)

    def button_count_type_poly_switch(self):
        if not objectstorage.button_bool["gt_line"]:
            objectstorage.button_bool["gt_polyline"] = not objectstorage.button_bool[
                "gt_polyline"
            ]
            print(objectstorage.button_bool["gt_polyline"])

    def button_count_type_line_switch(self):
        print("NOTHING HAPPENS CAUSE THIS BOTTON CAUSES PROBLEMS")
        # if not objectstorage.button_bool["gt_polyline"]:
        #     objectstorage.button_bool["gt_line"] = not objectstorage.button_bool[
        #         "gt_line"
        #     ]
        #     print(objectstorage.button_bool["gt_line"])
