import helpers.objectstorage as objectstorage


def fill_ground_truth(event, active_count_index=None):
    if objectstorage.active_countings[0].all_values_set():
        # change 0 to active_count_index
        # appends dataframe with values from dictionary

        objectstorage.ground_truth = objectstorage.ground_truth.append(
            objectstorage.active_countings[0].counted_vehicle_information(),
            ignore_index=True,
        )

        # delete finished object from active-list
        del objectstorage.active_countings[0]


def fill_background_dic(event, active_count_index=None):

    objectstorage.background_dic[
        objectstorage.active_countings[0].ID
    ] = objectstorage.active_countings[0].counted_vehicle_information()
