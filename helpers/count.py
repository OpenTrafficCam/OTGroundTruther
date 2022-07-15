import pandas as pd
import helpers.objectstorage as objectstorage

# import helpers.objectstorage as objectstorage


def initialize_new_count(event):
    """_summary_"""
    objectstorage.active_countings.append(current_count())


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
        self.Entry_Gate = "Placeholder"
        self.Entry_Frame = None
        self.Entry_Coordinate = None
        self.Exit_Gate = "Placeholder"
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

    def all_values_set(self):

        for key in self.counted_vehicle_information().keys():

            if (
                objectstorage.active_countings[0].counted_vehicle_information()[key]
                is None
            ):
                print(key + " is None")
                return False
        return True

    def __del__(self):
        print("Object with ID " + str(self.ID) + " deleted")
