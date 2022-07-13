import pandas as pd
import helpers.objectstorage as objectstorage

# import helpers.objectstorage as objectstorage


def initialize_new_count(event):
    """_summary_"""
    objectstorage.active_countings.append(current_count())
    print(objectstorage.active_countings)


class current_count:
    """_summary_

    Returns:
        _type_: _description_
    """

    counter = 0

    def __init__(self):
        type(self).counter += 1

        # Attributes
        self.ID = type(self).counter
        self.Vhc_class = None
        self.Entry_Gate = None
        self.Entry_Frame = None
        self.Entry_Coordinate = None
        self.Exit_Gate = None
        self.Exit_Frame = None
        self.Exit_Coordinate = None
        print("Anzahl der Instanzen: " + str(current_count.counter))

        self.first_coordinate = False

    def counted_vehicle_information(self):

        return {
            "ID": self.ID,
            "Class": self.Vhc_class,
            "Entry_Gate": self.Entry_Gate,
            "Entry_Frame": self.Entry_Frame,
            "Entry_Coordinate": self.Entry_Coordinate,
            "Exit_Gate": self.Exit_Gate,
            "Exit_Frame": self.Exit_Frame,
            "Exit_Coordinate": self.Exit_Coordinate,
        }


def assign_vehicle_class(event, active_count_index=None):
    if event.keysym == "c" and objectstorage.active_countings:
        print(
            "assigning Class Car to count: " + str(objectstorage.active_countings[0].ID)
        )

        # change 0 to active_count_index
        objectstorage.active_countings[0].Vhc_class = "Car"
        # print(vars(active_countings[0]))


def fill_ground_truth(event, active_count_index=None):

    # change 0 to active_count_index

    objectstorage.ground_truth = objectstorage.ground_truth.append(
        objectstorage.active_countings[0].counted_vehicle_information(),
        ignore_index=True,
    )

    print(objectstorage.ground_truth)