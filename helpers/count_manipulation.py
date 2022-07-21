import helpers.objectstorage as objectstorage


def assign_vehicle_class(event):

    active_count = objectstorage.active_countings[objectstorage.active_countings_index]

    if event.keysym == "c" and objectstorage.active_countings:
        print("assigning Class Car to count: " + str(active_count.ID))

        # change 0 to active_count_index
        active_count.Vhc_class = "Car"
        print(
            vars(objectstorage.active_countings[objectstorage.active_countings_index])
        )
