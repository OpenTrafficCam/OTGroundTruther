from matplotlib.patches import Polygon
import helpers.objectstorage as objectstorage
from tkinter import filedialog, messagebox
import json
import pandas as pd
import ast
from helpers.count import current_count
from tkinter.messagebox import askyesno


def fill_ground_truth(event):

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


def create_eventbased_dataframe():

    eventbased_dictionary = {}
    i = 0
    print(objectstorage.background_dic)
    # loop through background dic
    for track_id in objectstorage.background_dic.keys():

        # loop through gates
        for crossed_gate in objectstorage.background_dic[track_id]["Crossed_Gates"]:
            i += 1
            index = objectstorage.background_dic[track_id]["Crossed_Gates"].index(
                crossed_gate
            )
            print(index)
            eventbased_dictionary[i] = {
                "SectionID": crossed_gate,
                "TrackID": track_id,
                "Class": objectstorage.background_dic[track_id]["Class"],
                "X": objectstorage.background_dic[track_id]["Crossed_Coordinates"][
                    index
                ][0],
                "Y": objectstorage.background_dic[track_id]["Crossed_Coordinates"][
                    index
                ][1],
                "Frame": objectstorage.background_dic[track_id]["Crossed_Frames"][
                    index
                ],
            }

    return eventbased_dictionary


def eventased_dictionary_to_dataframe(eventbased_dictionary):
    """_summary_

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """

    objectstorage.eventbased_dataframe = pd.DataFrame.from_dict(
        eventbased_dictionary, orient="index"
    )
    objectstorage.eventbased_dataframe.index.set_names(["EventID"], inplace=True)

    objectstorage.eventbased_dataframe["seconds"] = (
        objectstorage.eventbased_dataframe["Frame"] / objectstorage.videoobject.fps
    )
    objectstorage.eventbased_dataframe["seconds"] = objectstorage.eventbased_dataframe[
        "seconds"
    ].astype("int")
    objectstorage.eventbased_dataframe["DateTime"] = pd.to_timedelta(
        objectstorage.eventbased_dataframe["seconds"], unit="seconds"
    )
    objectstorage.eventbased_dataframe["DateTime"] = (
        objectstorage.eventbased_dataframe["DateTime"]
        + objectstorage.videoobject.datetime_obj
    )
    # objectstorage.eventbased_dataframe = objectstorage.eventbased_dataframe.set_index(
    # "EventID"
    # )
    objectstorage.eventbased_dataframe.drop("seconds", axis=1, inplace=True)

    print(objectstorage.eventbased_dataframe)


def set_new_vehicle_counter():

    current_count.counter = objectstorage.background_dic[
        list(objectstorage.background_dic.keys())[-1]
    ]["ID"]

    print(
        "Nach import der GT startet die Zählung mit der ID: "
        + str(current_count.counter + 1)
    )


def dataframe_to_dict():

    objectstorage.background_dic = objectstorage.ground_truth.transpose().to_dict()

    for object_id in objectstorage.background_dic.keys():

        objectstorage.background_dic[object_id]["Entry_Coordinate"] = ast.literal_eval(
            objectstorage.background_dic[object_id]["Entry_Coordinate"]
        )
        objectstorage.background_dic[object_id]["Exit_Coordinate"] = ast.literal_eval(
            objectstorage.background_dic[object_id]["Exit_Coordinate"]
        )

        objectstorage.background_dic[object_id]["Crossed_Gates"] = ast.literal_eval(
            objectstorage.background_dic[object_id]["Crossed_Gates"]
        )
        objectstorage.background_dic[object_id]["Crossed_Frames"] = ast.literal_eval(
            objectstorage.background_dic[object_id]["Crossed_Frames"]
        )
        objectstorage.background_dic[object_id][
            "Crossed_Coordinates"
        ] = ast.literal_eval(
            objectstorage.background_dic[object_id]["Crossed_Coordinates"]
        )
    print(objectstorage.background_dic)


def load_gt_from_csv(treeview_gt, treeview_active_counts):

    if not objectstorage.ground_truth.empty:
        answer = askyesno(
            "Existing Ground Truth detected",
            "Work in process will be lost if you proceed!",
        )
        if answer:

            # set first coordinate to FALSE
            # reset background_dic
            objectstorage.background_dic = {}
            # clear treeview-gt
            # clear treeview-active_countings
            treeview_gt.delete(*treeview_gt.get_children())
            treeview_active_counts.delete(*treeview_active_counts.get_children())

            # reset active_countings
            objectstorage.active_countings = []
            # reset active_countings_index
            objectstorage.active_countings_index = 0

    file_path = filedialog.askopenfilename()

    # safe path for quick safe later
    objectstorage.quicksafe_filepath_gt = file_path
    objectstorage.ground_truth = pd.read_csv(
        file_path,
    )

    objectstorage.ground_truth.reset_index(drop=False, inplace=True)

    objectstorage.ground_truth["index"] = objectstorage.ground_truth["index"] + 1
    objectstorage.ground_truth.set_index("index", inplace=True)
    dataframe_to_dict()
    set_new_vehicle_counter()


def safe_gt_to_csv():
    file_path_gt = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")]
    )
    # index=False ==> prevent creating extra index col
    objectstorage.ground_truth.to_csv(file_path_gt, index=False)

    # safe path for quick safe later
    objectstorage.quicksafe_filepath_gt = file_path_gt

    answer = askyesno(
        "Eventbased data",
        "Create eventbased data?",
    )
    if answer:

        file_path_event = filedialog.asksaveasfilename(
            defaultextension=".csv", filetypes=[("CSV", "*.csv")]
        )

        objectstorage.quicksafe_filepath_event = file_path_event

        # create eventbased dictionary
        eventbased_dictionary = create_eventbased_dataframe()
        # create dataframe from eventbased Dictionary
        eventased_dictionary_to_dataframe(eventbased_dictionary)

        # safe dataframe to csv with filepath for eventbased dataframe
        objectstorage.eventbased_dataframe.to_csv(file_path_event, index=True)


def quick_safe_to_csv(event):
    if objectstorage.quicksafe_filepath_gt:
        objectstorage.ground_truth.to_csv(objectstorage.quicksafe_filepath_gt)
    if objectstorage.quicksafe_filepath_event:
        objectstorage.eventbased_dataframe.to_csv(
            objectstorage.quicksafe_filepath_event
        )
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
        #            del objectstorage.flow_dict["Detectors"][detector]["Geometry_polygon"]

        json.dump(objectstorage.flow_dict, file, indent=4)
    else:
        info_message("Warning", "Create Sections and Movements first!")


def info_message(title, text):

    return messagebox.showinfo(title=title, message=text)
