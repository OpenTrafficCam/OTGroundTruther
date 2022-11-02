import helpers.filehelper.objectstorage as objectstorage

vehicle_definition = {
    "1": "Car",
    "2": "Bycicle",
    "3": "Person",
    "4": "Bus",
    "5": "Van",
    "6": "Truck",
    "7": "Motorcycle",
    "8": "Trailortruck",
}


def assign_vehicle_class(event):

    if not objectstorage.active_countings:
        return
    active_count = objectstorage.active_countings[objectstorage.active_countings_index]

    active_count.Vhc_class = vehicle_definition[event.keysym]
    print(
        f"assigning Class {vehicle_definition[event.keysym]} to count: "
        + str(active_count.ID)
    )
