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

        # if last active count is finished make active makeable via mouse click
        if not objectstorage.active_countings:
            objectstorage.config_dict["count_active"] = False

        print(objectstorage.ground_truth)


def fill_eventbased_dictionary(event):
    
    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        active_count = objectstorage.active_countings[objectstorage.active_countings_index]

        for crossed_gate, crossed_coordinate, crossed_frame in zip(active_count.Gates, active_count.Coordinates, active_count.Frames):

            objectstorage.eventbased_dictionary_index += 1          

            objectstorage.eventbased_dictionary[str(objectstorage.eventbased_dictionary_index)] = {"SectionID": crossed_gate,"TrackID": active_count.ID, "X":crossed_coordinate[0],"Y":crossed_coordinate[1], "Frame":crossed_frame, "Class": active_count.Vhc_class}

def eventased_dictionary_to_dataframe():
    """_summary_

    Args:
        eventbased_dictionary (dic): dictionary with frame and belonging events

    Returns:
        dataframe: dataframe with events and belonging datetime
    """

    eventbased_dataframe = pd.DataFrame.from_dict(
        objectstorage.eventbased_dictionary, orient="index"
    )
    eventbased_dataframe.index.set_names(["EventID"], inplace=True)

    eventbased_dataframe["seconds"] = (
        eventbased_dataframe["Frame"] / objectstorage.videoobject.fps
    )
    eventbased_dataframe["seconds"] = eventbased_dataframe[
        "seconds"
    ].astype("int")
    eventbased_dataframe["DateTime"] = pd.to_timedelta(
        eventbased_dataframe["seconds"], unit="seconds"
    )
    eventbased_dataframe["DateTime"] = (
        eventbased_dataframe["DateTime"]
        + objectstorage.videoobject.datetime_obj
    )

    eventbased_dataframe.drop("seconds", axis=1, inplace=True)

    return eventbased_dataframe

def set_new_vehicle_counter(eventbased_dataframe):

    current_count.counter = eventbased_dataframe["TrackID"].max()

    print(
        "Nach import der GT startet die Zählung mit der ID: "
        + str(current_count.counter + 1)
    )

def load_event_dic_from_csv(treeview_gt, treeview_active_counts):

    if not objectstorage.ground_truth.empty:
        answer = askyesno(
            "Existing Ground Truth detected",
            "Work in process will be lost if you proceed!",
        )
        if answer:

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
    eventbased_dataframe.drop(['DateTime'], axis=1, inplace=True)

    eventbased_dataframe.set_index("EventID" , drop=True, inplace=True)

    #create dictionary from csv
    objectstorage.eventbased_dictionary = eventbased_dataframe.to_dict('index')

    dic_to_gt_dataframe()

    #set counter with last tracknumber 
    set_new_vehicle_counter(eventbased_dataframe)


def dic_to_gt_dataframe():  # sourcery skip: avoid-builtin-shadow
    #create dataframe
    ground_truth_dic = {}

    for event in objectstorage.eventbased_dictionary:
        id = objectstorage.eventbased_dictionary[event]["TrackID"]
        if objectstorage.eventbased_dictionary[event]["TrackID"] not in ground_truth_dic:
            
            ground_truth_dic[objectstorage.eventbased_dictionary[event]["TrackID"]] = {"Class": [], "Crossed_Gates": [], "Crossed_Frames": [], "Crossed_Coordinates": []}
            ground_truth_dic[id]["Class"] = objectstorage.eventbased_dictionary[event]["Class"]

        ground_truth_dic[id]["Crossed_Gates"].append(objectstorage.eventbased_dictionary[event]["SectionID"])
        ground_truth_dic[id]["Crossed_Frames"].append(objectstorage.eventbased_dictionary[event]["Frame"])
        ground_truth_dic[id]["Crossed_Coordinates"].append((objectstorage.eventbased_dictionary[event]["X"],objectstorage.eventbased_dictionary[event]["Y"]))

    objectstorage.ground_truth = pd.DataFrame.from_dict(ground_truth_dic, orient="index")
    objectstorage.ground_truth.reset_index(inplace=True)
    objectstorage.ground_truth.rename({'index': 'ID'}, axis=1, inplace=True)
    

def safe_eventbased_dataframe():

    #create dataframe from dictionary
    eventbased_dataframe = eventased_dictionary_to_dataframe()

    file_path_eventbased = filedialog.asksaveasfilename(
        defaultextension=".csv", filetypes=[("CSV", "*.csv")]
    )

    objectstorage.quicksafe_filepath_event = file_path_eventbased

    eventbased_dataframe.to_csv(file_path_eventbased, index=True)


# def quick_safe_to_csv(event):
#     if objectstorage.quicksafe_filepath_gt:
#         objectstorage.ground_truth.to_csv(
#             objectstorage.quicksafe_filepath_gt, index=False
#         )
#     else:
#         info_message("Warning", "Safe groundtruth first to set filepath!")

#     # if eventdataframe was safed one, then use the path for quick saving
#     if objectstorage.quicksafe_filepath_event:
#         # create eventbased dictionary
#         eventbased_dictionary = create_eventbased_dictionary()
#         # create dataframe from eventbased Dictionary
#         eventased_dictionary_to_dataframe(eventbased_dictionary)

#         objectstorage.eventbased_dataframe.to_csv(
#             objectstorage.quicksafe_filepath_event, index=True
#         )
#     else:
#         info_message("Warning", "Safe eventbased csv first to set filepath!")

#         return

#     info_message("Info", "qicksafed")


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

        json.dump(objectstorage.flow_dict, file, indent=4)
    else:
        info_message("Warning", "Create Sections and Movements first!")


def info_message(title, text):

    return messagebox.showinfo(title=title, message=text)
