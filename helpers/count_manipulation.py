import helpers.objectstorage as objectstorage


def assign_vehicle_class(event):

    if not objectstorage.active_countings:
        return
    active_count = objectstorage.active_countings[objectstorage.active_countings_index]

    if event.keysym == "c":
        print("assigning Class Car to count: " + str(active_count.ID))

        # change 0 to active_count_index
        active_count.Vhc_class = "Car"

    if event.keysym == "b":
        print("assigning Class Car to count: " + str(active_count.ID))

        # change 0 to active_count_index
        active_count.Vhc_class = "Bicycle"

    if event.keysym == "t":
        print("assigning Class Car to count: " + str(active_count.ID))

        # change 0 to active_count_index
        active_count.Vhc_class = "Truck"
