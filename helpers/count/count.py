import helpers.filehelper.objectstorage as objectstorage

def initialize_new_count(event):
    """_summary_"""
    # if pressed key is n or there are no active counts (for creating active count by mouseclick)
    if event.keysym_num == 110 or not objectstorage.config_dict["count_active"]:

        objectstorage.active_countings.append(current_count())

        if len(objectstorage.active_countings) > 1:
            # define index
            # stay at latest created vehicle
            objectstorage.active_countings_index = (
                len(objectstorage.active_countings) - 1
            )
        else:
            return

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
        self.Gates = []
        self.Frames = []
        self.Coordinates = []
        self.Valid_count = False

        print("Anzahl der Instanzen: " + str(current_count.counter))

    def counted_vehicle_information(self):

        return {
            "ID": self.ID,
            "Class": self.Vhc_class,
            "Crossed_Gates": self.Gates,
            "Crossed_Frames": self.Frames,
            "Crossed_Coordinates": self.Coordinates,
        }

    def all_values_set(self):


        for key in self.counted_vehicle_information().keys():
            if not(
                objectstorage.active_countings[
                    objectstorage.active_countings_index
                ].counted_vehicle_information()[key]
            ):
                print(key + " is None")
                return False
            

        return True

    def __del__(self):
        print("Object with ID " + str(self.ID) + " deleted")
