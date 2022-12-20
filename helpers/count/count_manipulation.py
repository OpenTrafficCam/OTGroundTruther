import helpers.filehelper.objectstorage as objectstorage
from helpers.filehelper.config import vehicle_definition


def assign_vehicle_class(event):

    if not objectstorage.active_countings:
        return
    active_count = objectstorage.active_countings[objectstorage.active_countings_index]

    active_count.Vhc_class = vehicle_definition[event.keysym]
    print(event.keysym)
    print(
        f"assigning Class {vehicle_definition[event.keysym]} to count: "
        + str(active_count.ID)
    )
    
