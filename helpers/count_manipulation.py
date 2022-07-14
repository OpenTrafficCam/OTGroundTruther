import helpers.objectstorage as objectstorage


def assign_vehicle_class(event, active_count_index=None):
    if event.keysym == "c" and objectstorage.active_countings:
        print(
            "assigning Class Car to count: " + str(objectstorage.active_countings[0].ID)
        )

        # change 0 to active_count_index
        objectstorage.active_countings[0].Vhc_class = "Car"
        # print(vars(active_countings[0]))
