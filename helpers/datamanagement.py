import helpers.objectstorage as objectstorage


def fill_ground_truth(event, active_count_index=None):
    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        # change 0 to active_count_index
        # appends dataframe with values from dictionary

        objectstorage.ground_truth = objectstorage.ground_truth.append(
            objectstorage.active_countings[
                objectstorage.active_countings_index
            ].counted_vehicle_information(),
            ignore_index=True,
        )

        # delete finished object from active-list
        del objectstorage.active_countings[objectstorage.active_countings_index]


def fill_background_dic(event):
    if (
        objectstorage.active_countings
        and objectstorage.active_countings[
            objectstorage.active_countings_index
        ].all_values_set()
    ):
        objectstorage.background_dic[
            objectstorage.active_countings[objectstorage.active_countings_index].ID
        ] = objectstorage.active_countings[
            objectstorage.active_countings_index
        ].counted_vehicle_information()
