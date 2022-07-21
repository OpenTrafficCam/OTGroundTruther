import tkinter as tk
import tkinter.ttk as ttk
import helpers.objectstorage as objectstorage


class FrameGT(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Ground Truth", **kwargs)
        self.frame_controls = tk.Frame(master=self)
        self.frame_controls.pack(
            fill="x",
        )

        # Files treeview
        self.tree_gt = ttk.Treeview(master=self.frame_controls, height=3)
        self.tree_gt.pack(
            fill="x",
            padx=10,
            pady=10,
        )

        self.tree_gt.bind(
            "<<TreeviewSelect>>",  # self.tree_detector_selection
        )

        tree_files_cols = {
            "#0": "ID",
            "Class": "Class",
        }

        self.tree_gt["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_gt.column("#0", anchor="center", width=50)
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
