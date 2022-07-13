import tkinter as tk
import tkinter.ttk as ttk


class FrameActiveCounts(tk.LabelFrame):
    def __init__(self, **kwargs):
        super().__init__(text="Active counts", **kwargs)
        self.frame_controls = tk.Frame(master=self)
        self.frame_controls.pack(
            fill="x",
        )

        # Files treeview
        self.tree_active_countings = ttk.Treeview(master=self.frame_controls, height=3)
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
        }
        self.tree_active_countings["columns"] = tuple(
            {k: v for k, v in tree_files_cols.items() if k != "#0"}.keys()
        )
        self.tree_active_countings.column("#0", anchor="center", width=50)
        self.tree_active_countings.heading(
            "#0", text=tree_files_cols["#0"], anchor="center"
        )
        self.tree_active_countings.column("Class", anchor="center")
        self.tree_active_countings.heading(
            "Class", text=tree_files_cols["Class"], anchor="center"
        )

        # create file
        # self.button_add_gt_file = tk.Button(
        #     master=self.frame_controls,
        #     width=12,
        #     text="Create new file",
        # )
        # self.button_add_gt_file.grid(row=0, column=0, pady=(10, 0), sticky="ew")
