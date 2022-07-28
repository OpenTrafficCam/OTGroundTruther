from matplotlib.patches import Polygon
import helpers.objectstorage as objectstorage
from tkinter import filedialog, messagebox
import json


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

    messagebox.showinfo(title=title, message=text)
