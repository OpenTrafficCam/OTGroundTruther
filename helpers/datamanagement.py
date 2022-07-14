import helpers.objectstorage as objectstorage


def fill_ground_truth(event, active_count_index=None):

    # change 0 to active_count_index
    # appends dataframe with values from dictionary

    objectstorage.ground_truth = objectstorage.ground_truth.append(
        objectstorage.active_countings[0].counted_vehicle_information(),
        ignore_index=True,
    )

    print("Number of active counts" + str(len(objectstorage.active_countings)))
    print(objectstorage.ground_truth)


def fill_background_dic(event, active_count_index=None):

    objectstorage.background_dic[
        objectstorage.active_countings[0].ID
    ] = objectstorage.active_countings[0].counted_vehicle_information()

    print(objectstorage.background_dic)

    # delete finished object from active-list
    del objectstorage.active_countings[0]