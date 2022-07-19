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

        self.tree_active_countings.bind(
            "<<TreeviewSelect>>",  # self.tree_detector_selection
        )

        tree_files_cols = {
            "#0": "ID",
            "Class": "Class",
            "Start": "Start",
            "End": "End",
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
        self.frame_control_active_counts = tk.Frame(master=self)
        self.frame_control_active_counts.pack()

        self.button_count_polyline = tk.Button(
            master=self.frame_control_active_counts,
            width=12,
            text="Polyline",
        )
        self.button_count_polyline.grid(row=0, column=0, padx=(10, 0))

        self.button_count_line = tk.Button(
            master=self.frame_control_active_counts,
            width=12,
            text="Line",
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
            ),
        )

    def update_treeview(self, event, active_count_index=None):
        # selected_item = self.tree_active_countings.selection()[0]
        # print(selected_item)
        # make selectable
        if objectstorage.active_countings:
            count_ID = objectstorage.active_countings[0].ID

            count = objectstorage.active_countings[0]

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
                        ),
                    )
            objectstorage.active_countings[0].intersection_list(self)

    def delete_from_treeview(self, event, active_count_index=None):
        # make selectable
        if (
            objectstorage.active_countings
            and objectstorage.active_countings[0].all_values_set()
        ):
            count_ID = objectstorage.active_countings[0].ID

            children = self.tree_active_countings.get_children("")
            for child in children:
                values = self.tree_active_countings.item(child, "text")
                if count_ID == values:
                    self.tree_active_countings.delete(child)

        # item = objectstorage.active_countings[0].ID
        # print(item)
        # item_text = self.tree_active_countings.item(selected_item, "text")
        # print(item_text)
        # self.tree_active_countings.item(item, text="blub", values=("foo", "bar"))

    # create file
    # self.button_add_gt_file = tk.Button(
    #     master=self.frame_controls,
    #     width=12,
    #     text="Create new file",
    # )
    # self.button_add_gt_file.grid(row=0, column=0, pady=(10, 0), sticky="ew")
