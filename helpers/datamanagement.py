from matplotlib.patches import Polygon
import helpers.objectstorage as objectstorage
from tkinter import filedialog, messagebox
import json
import pandas as pd


def fill_ground_truth(event, active_count_index=None):
    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        # change 0 to active_count_index
        # appends dataframe with values from dictionary

        objectstorage.ground_truth = objectstorage.ground_truth.append(
            objectstorage.active_countings[
                objectstorage.active_countings_index
            ].counted_vehicle_information(),
            ignore_index=True,
        )

        # delete finished object from active-list
        del objectstorage.active_countings[objectstorage.active_countings_index]


def fill_background_dic(event):
    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        objectstorage.background_dic[
            objectstorage.active_countings[objectstorage.active_countings_index].ID
        ] = objectstorage.active_countings[
            objectstorage.active_countings_index
        ].counted_vehicle_information()


def dataframe_to_dict():

    objectstorage.background_dic = (
        objectstorage.ground_truth.set_index("ID").transpose().to_dict()
    )

    # objectstorage.background_dic = calc_dataframe.groupby("ID").to_dict()


def create_ground_truth_dataframe():
    pass


def load_gt_from_csv():

    file_path = filedialog.askopenfilename()

    # safe path for quick safe later
    objectstorage.quicksafe_filepath = file_path
    objectstorage.ground_truth = pd.read_csv(
        file_path,
    )
    dataframe_to_dict()


def safe_gt_to_csv():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")]
    )

    # safe path for quick safe later
    objectstorage.quicksafe_filepath = file_path
    # index=False ==> prevent creating extra index col
    objectstorage.ground_truth.to_csv(file_path, index=False)


def quick_safe_to_csv(event):
    if objectstorage.quicksafe_filepath:
        objectstorage.ground_truth.to_csv(objectstorage.quicksafe_filepath)
        info_message("Info", "qicksafed")

    else:
        info_message("Warning", "Safe groundtruth first!")


def load_flowfile():
    """Loads flow file.

    Returns:
        json: Return json file to read from.
    """

    if (
        not objectstorage.flow_dict["Detectors"]
        and not objectstorage.flow_dict["Movements"]
    ):
        filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
        files = open(filepath.name, "r")
        files = files.read()

        return json.loads(files)

    else:
        info_message("Warning", "Clear existing flowfile first!")


def save_flowfile():
    """Save created dictionary with detectors
    and movements.

    Args:
        flow_dict (dictionary): Dictionary with sections and movements.
    """
    if objectstorage.flow_dict["Detectors"]:
        files = [("Files", "*.otflow")]
        file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)

        # delete shapeley objects because they cant be safed
        for detector in objectstorage.flow_dict["Detectors"]:
            del objectstorage.flow_dict["Detectors"][detector]["Geometry_line"]
            del objectstorage.flow_dict["Detectors"][detector]["Geometry_polygon"]

        json.dump(objectstorage.flow_dict, file, indent=4)
    else:
        info_message("Warning", "Create Sections and Movements first!")


def info_message(title, text):

    return messagebox.showinfo(title=title, message=text)
