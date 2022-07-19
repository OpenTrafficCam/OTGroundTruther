import helpers.objectstorage as objectstorage
from shapely.geometry import Polygon, LineString, Point
import geopandas
import pandas as pd


# import helpers.objectstorage as objectstorage


def initialize_new_count(event):
    """_summary_"""
    objectstorage.active_countings.append(current_count())


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
        }

    def all_values_set(self):

        for key in self.counted_vehicle_information().keys():

            if (
                objectstorage.active_countings[0].counted_vehicle_information()[key]
                is None
            ):
                print(key + " is None")
                return False
        return True

    def intersection_list(self, event):
        # only do when at least two points exist or at least the second point.
        if (
            not objectstorage.button_bool["linedetector_toggle"]
            and self.Exit_Coordinate is not None
        ):

            geoobjects = [
                objectstorage.flow_dict["Detectors"][k]["Geometry_polygon"]
                for k, v in objectstorage.flow_dict["Detectors"].items()
            ]

            s = geopandas.GeoSeries(geoobjects)

            dataframe = pd.DataFrame(data=s)
            dataframe["Detector"] = objectstorage.flow_dict["Detectors"]
            dataframe["Intersects"] = s.intersects(
                LineString([self.Entry_Coordinate, self.Exit_Coordinate])
            )
            print(dataframe)
            return list(dataframe["Detector"][dataframe["Intersects"] == True])

    def __del__(self):
        print("Object with ID " + str(self.ID) + " deleted")
