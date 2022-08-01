import helpers.objectstorage as objectstorage
from shapely.geometry import Polygon, LineString, Point
import geopandas
import pandas as pd


# import helpers.objectstorage as objectstorage


def initialize_new_count(event):
    """_summary_"""
    objectstorage.active_countings.append(current_count())

    if len(objectstorage.active_countings) > 1:
        objectstorage.active_countings_index = len(objectstorage.active_countings) - 1
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
        self.Entry_Gate = "Placeholder"
        self.Entry_Frame = None
        self.Entry_Coordinate = None
        self.Exit_Gate = "Placeholder"
        self.Exit_Frame = None
        self.Exit_Coordinate = None
        self.All_Coordinates = []
        self.All_Coordinates_Frames = []
        self.Type = None
        self.Crossed_gates = []
        print("Anzahl der Instanzen: " + str(current_count.counter))

        self.first_coordinate = False

    def counted_vehicle_information(self):

        return {
            "ID": self.ID,
            "Class": self.Vhc_class,
            "Entry_Gate": self.Entry_Gate,
            "Entry_Frame": self.Entry_Frame,
            "Entry_Coordinate": self.Entry_Coordinate,
            "Exit_Gate": self.Exit_Gate,
            "Exit_Frame": self.Exit_Frame,
            "Exit_Coordinate": self.Exit_Coordinate,
            "All_Coordinates": self.All_Coordinates,
            "All_Coordinates_Frames": self.All_Coordinates_Frames,
            "GT_Type": self.Type,
            "Crossed_gates": self.Crossed_gates,
        }

    def all_values_set(self):

        for key in self.counted_vehicle_information().keys():

            if (
                objectstorage.active_countings[
                    objectstorage.active_countings_index
                ].counted_vehicle_information()[key]
                is None
            ):
                print(key + " is None")
                return False
        return True

    def get_intersect_and_frame(self, event):
        """Calculates if trajectorie of vehicle crosses any section. Returns crossed Gate and Frame when crossed as list of tuples.
            Problem cant detect if vehicle crosses gate a second time
        Args:
            event (_type_): gets triggered when when class or coordinate is changed.
        """
        # only do when at least two points exist or at least the second point.
        if objectstorage.button_bool["linedetector_toggle"] or not self.Exit_Coordinate:
            return
        geoobjects = [
            objectstorage.flow_dict["Detectors"][k]["Geometry_polygon"]
            for k, v in objectstorage.flow_dict["Detectors"].items()
        ]

        s = geopandas.GeoSeries(geoobjects)

        dataframe = pd.DataFrame(data=s)
        dataframe["Detector"] = objectstorage.flow_dict["Detectors"]

        if self.Type == "Line":
            lineobject = LineString([self.Entry_Coordinate, self.Exit_Coordinate])

        else:
            try:
                lineobject = LineString(self.All_Coordinates[-2:])
            except ValueError:
                print(
                    "Cant calculate intersection, LineStrings must have at least 2 coordinate tuples"
                )
                return

        dataframe["Intersects"] = s.intersects(lineobject)

        list_of_crossed_gates = list(
            dataframe["Detector"][dataframe["Intersects"] == True]
        )
        for gate in list_of_crossed_gates:
            # if gate is already in tuple of crossed gates than break
            # unless vehicle crosses gate in a different frame
            if not (
                bool(
                    [
                        item
                        for item in self.Crossed_gates
                        if item[0] == gate
                        and item[1] == objectstorage.videoobject.current_frame
                    ]
                )
            ):
                self.Crossed_gates.append(
                    (gate, objectstorage.videoobject.current_frame)
                )

    def __del__(self):
        print("Object with ID " + str(self.ID) + " deleted")
