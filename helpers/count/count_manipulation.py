import helpers.filehelper.objectstorage as objectstorage

vehicle_definition = {
    "1": "Pkw ohne Anhänger",
    "3": "Fahrrad ohne Anhänger",
    "2": "Person",
    "4": "Bus",
    "5": "Lkw ohne Anhänger",
    "6": "Lkw mit Anhänger",
    "7": "Pkw mit Anhänger",
    "8": "Lieferwagen ohne Anhänger",
    "9": "Lieferwagen mit Anhänger",
    "equal": "Motorisierte Zweiräder",
    "exclam":"Scooter",
    "quotedbl": "Lastenrad",
    "section": "Fahrrad mit Anhänger",
    "percent":"Schienenfahrzeug"
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
