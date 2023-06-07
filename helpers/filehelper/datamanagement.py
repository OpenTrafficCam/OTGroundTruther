import json
from tkinter import filedialog, messagebox
from tkinter.messagebox import askyesno

import pandas as pd

import helpers.filehelper.objectstorage as objectstorage
from helpers.count.count import current_count
from helpers.filehelper.config import meta_data_dict


def fill_ground_truth(event):
    """adds track to ground truth dataframe, only necessary to draw tracks

    Args:
        event (tkinter.event): Return button adds to groundtruth if all values of count
        are set.
    """
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

        # if last active count is finished make active makeable via mouse click
        if not objectstorage.active_countings:
            objectstorage.config_dict["count_active"] = False

        print(objectstorage.ground_truth)


def fill_eventbased_dictionary(event):
    """Fills dictionary according to event

    Args:
        event (tkinter.event): Return button adds to eventbased dictionary if all
        values of count are set.
    """

    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        active_count = objectstorage.active_countings[
            objectstorage.active_countings_index
        ]

        for crossed_gate, crossed_coordinate, crossed_frame in zip(
            active_count.Gates, active_count.Coordinates, active_count.Frames
        ):

            objectstorage.eventbased_dictionary_index += 1

            objectstorage.eventbased_dictionary[
                str(objectstorage.eventbased_dictionary_index)
            ] = {
                "SectionID": crossed_gate,
                "TrackID": active_count.ID,
                "X": crossed_coordinate[0],
                "Y": crossed_coordinate[1],
                "Frame": crossed_frame,
                "Class": active_count.Vhc_class,
                "Vidfilename": active_count.Vid_filename,
            }


def eventased_dictionary_to_dataframe():
    """Creates a dataframe to later be safed as csv

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """
    # endtime = round(time.time() - objectstorage.starttime)

    # objectstorage.eventbased_dictionary["999"] = {
    #     "SectionID": str(endtime),
    #     "TrackID": None,
    #     "X": 1,
    #     "Y": 1,
    #     "Frame": 1,
    #     "Class": "Car",
    #     "Vidfilename": "file",
    # }

    eventbased_dataframe = pd.DataFrame.from_dict(
        objectstorage.eventbased_dictionary, orient="index"
    )
    print(eventbased_dataframe)
    eventbased_dataframe.index.set_names(["EventID"], inplace=True)

    eventbased_dataframe["seconds"] = (
        eventbased_dataframe["Frame"] / objectstorage.videoobject.fps
    )
    eventbased_dataframe["seconds"] = eventbased_dataframe["seconds"].astype("int")
    eventbased_dataframe["DateTime"] = pd.to_timedelta(
        eventbased_dataframe["seconds"], unit="seconds"
    )
    eventbased_dataframe["DateTime"] = (
        eventbased_dataframe["DateTime"] + objectstorage.videoobject.datetime_obj
    )

    eventbased_dataframe.drop("seconds", axis=1, inplace=True)

    return eventbased_dataframe


def set_new_vehicle_counter(eventbased_dataframe):
    """Sets to counter ID according to the max value of the trackID imported from the
    event csv

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events
    """

    current_count.counter = eventbased_dataframe["TrackID"].max()

    print(
        "Nach import der GT startet die Zählung mit der ID: "
        + str(current_count.counter + 1)
    )


def load_event_dic_from_csv(treeview_gt, treeview_active_counts):
    """Function to create the eventbased dictionary and dataframe

    Args:
        treeview_gt (_type_): treeview with gt
        treeview_active_counts (_type_): treeview with active_countings
    """

    if not objectstorage.ground_truth.empty:
        answer = askyesno(
            "Existing Ground Truth detected",
            "Work in process will be lost if you proceed!",
        )
        if not answer:
            return

        # set first coordinate to FALSE
        # reset background_dic
        # clear treeview-gt
        # clear treeview-active_countings
        treeview_gt.delete(*treeview_gt.get_children())
        treeview_active_counts.delete(*treeview_active_counts.get_children())

        # reset active_countings
        objectstorage.active_countings = []
        # reset active_countings_index
        objectstorage.active_countings_index = 0

        objectstorage.config_dict["count_active"] = False

    file_path = filedialog.askopenfilename()

    # safe path for quick safe later
    objectstorage.quicksafe_filepath_event = file_path

    eventbased_dataframe = pd.read_csv(
        file_path,
    )
    eventbased_dataframe.drop(["DateTime"], axis=1, inplace=True)

    objectstorage.eventbased_dictionary_index = eventbased_dataframe["EventID"].max()

    eventbased_dataframe.set_index("EventID", drop=True, inplace=True)

    # create dictionary from csv
    objectstorage.eventbased_dictionary = eventbased_dataframe.to_dict("index")

    dic_to_gt_dataframe()

    # set counter with last tracknumber
    set_new_vehicle_counter(eventbased_dataframe)

    # since the filling treeview functions is called// treeview needs to get wiped out
    treeview_gt.delete(*treeview_gt.get_children())


def dic_to_gt_dataframe():
    """Create dataframe from dictionary"""

    # create dataframe
    ground_truth_dic = {}

    for event in objectstorage.eventbased_dictionary:
        id = objectstorage.eventbased_dictionary[event]["TrackID"]
        if (
            objectstorage.eventbased_dictionary[event]["TrackID"]
            not in ground_truth_dic
        ):

            ground_truth_dic[objectstorage.eventbased_dictionary[event]["TrackID"]] = {
                "Class": [],
                "Crossed_Gates": [],
                "Crossed_Frames": [],
                "Crossed_Coordinates": [],
            }
            ground_truth_dic[id]["Class"] = objectstorage.eventbased_dictionary[event][
                "Class"
            ]

        if (
            not ground_truth_dic[id]["Crossed_Frames"]
            or objectstorage.eventbased_dictionary[event]["Frame"]
            < ground_truth_dic[id]["Crossed_Frames"][-1]
        ):
            ground_truth_dic[id]["Crossed_Gates"].insert(
                0, objectstorage.eventbased_dictionary[event]["SectionID"]
            )
            ground_truth_dic[id]["Crossed_Frames"].insert(
                0, objectstorage.eventbased_dictionary[event]["Frame"]
            )
            ground_truth_dic[id]["Crossed_Coordinates"].insert(
                0,
                (
                    # hier muss die umrechnung mit x faktor geschehen
                    objectstorage.eventbased_dictionary[event]["X"],
                    # hier muss die umrechnung mit y faktor geschehen
                    objectstorage.eventbased_dictionary[event]["Y"],
                ),
            )

        else:
            ground_truth_dic[id]["Crossed_Gates"].append(
                objectstorage.eventbased_dictionary[event]["SectionID"]
            )
            ground_truth_dic[id]["Crossed_Frames"].append(
                objectstorage.eventbased_dictionary[event]["Frame"]
            )
            ground_truth_dic[id]["Crossed_Coordinates"].append(
                (
                    # hier muss die umrechnung mit x faktor geschehen
                    objectstorage.eventbased_dictionary[event]["X"],
                    # hier muss die umrechnung mit y faktor geschehen
                    objectstorage.eventbased_dictionary[event]["Y"],
                )
            )

    objectstorage.ground_truth = pd.DataFrame.from_dict(
        ground_truth_dic, orient="index"
    )
    objectstorage.ground_truth.reset_index(inplace=True)
    objectstorage.ground_truth.rename({"index": "ID"}, axis=1, inplace=True)
    print(objectstorage.ground_truth["Crossed_Frames"])


def safe_eventbased_dataframe():
    """First creates dataframe and than csv"""

    # create dataframe from dictionary
    eventbased_dataframe = eventased_dictionary_to_dataframe()

    file_path_eventbased = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")]
    )

    objectstorage.quicksafe_filepath_event = file_path_eventbased

    eventbased_dataframe.to_csv(file_path_eventbased, index=True)


def quick_safe_to_csv(event):

    eventbased_dataframe = eventased_dictionary_to_dataframe()

    if objectstorage.quicksafe_filepath_event:
        eventbased_dataframe.to_csv(objectstorage.quicksafe_filepath_event, index=True)
        info_message("Warning", "Quicksafed!")
    else:
        info_message("Warning", "Safe events first to set filepath!")


# def load_flowfile():
#     """Loads flow file.

#     Returns:
#         json: Return json file to read from.
#     """

#     if (
#         not objectstorage.flow_dict["Detectors"]
#         and not objectstorage.flow_dict["Movements"]
#     ):
#         filepath = filedialog.askopenfile(filetypes=[("Detectors", "*.OTflow")])
#         files = open(filepath.name, "r")
#         files = files.read()

#         return json.loads(files)

#     else:
#         info_message("Warning", "Clear existing flowfile first!")


def load_flowfile():
    """Loads flow file.

    Returns:
        json: Return json file to read from.
    """
    if (
            not objectstorage.flow_dict["Sections"]):
        filepath = filedialog.askopenfile(filetypes=[("Sections", "*.OTflow")])
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
    if objectstorage.flow_dict["Sections"]:
        files = [("Files", "*.otflow")]
        file = filedialog.asksaveasfile(filetypes=files, defaultextension=files)

        flow_dic_for_saving = {"metadata": None, "Sections": []}

        # delete shapeley objects because they cant be safed
        for detector in objectstorage.flow_dict["Sections"]:
            del detector["Geometry_line"]

            x1 = int(
                detector["coordinates"][0]["x"] / objectstorage.videoobject.x_resize_factor)
            y1 = int(
                detector["coordinates"][0]["y"] / objectstorage.videoobject.y_resize_factor)
            x2 = int(
                detector["coordinates"][1]["x"] / objectstorage.videoobject.x_resize_factor)
            y2 = int(
                detector["coordinates"][1]["y"] / objectstorage.videoobject.y_resize_factor)

            # add altered sections to new section dic for safing
            flow_dic_for_saving["Sections"].append({"id": detector["id"], "type": "line",
                                                    "relative_offset_coordinates": {"section-enter": {"x": 0.5, "y": 0.5}},
                                                    "coordinates": [{"x": x1, "y": y1}, {"x": x2, "y": y2}], "plugin_data": {}})

        flow_dic_for_saving = add_meta_data(flow_dic_for_saving)

        json.dump(flow_dic_for_saving, file)
    else:
        info_message("Warning", "Create Sections and Movements first!")


def add_meta_data(flow_dic):
    # adds meta data dic
    flow_dic["metadata"] = meta_data_dict["metadata"]
    flow_dic["metadata"]["video"]["name"] = objectstorage.videoobject.filename.split(".")[
        0]
    flow_dic["metadata"]["video"]["width"] = objectstorage.videoobject.videowidth
    flow_dic["metadata"]["video"]["height"] = objectstorage.videoobject.videoheight

    return flow_dic


def info_message(title, text):

    return messagebox.showinfo(title=title, message=text)
