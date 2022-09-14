import helpers.objectstorage as objectstorage
from shapely.geometry import Polygon, LineString, Point
import geopandas
import pandas as pd


# import helpers.objectstorage as objectstorage


def initialize_new_count(event):
    """_summary_"""
    # if pressed key is n or there are no active counts (for creating active count by mouseclick)
    if event.keysym_num == 110 or not objectstorage.config_dict["count_active"]:

        objectstorage.active_countings.append(current_count())

        if len(objectstorage.active_countings) > 1:
            # define index
            # stay at latest created vehicle
            objectstorage.active_countings_index = (
                len(objectstorage.active_countings) - 1
            )
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
        # self.All_Coordinates = []
        # self.All_Coordinates_Frames = []
        self.Crossed_Gates = []
        self.Crossed_Frames = []
        self.Crossed_Gates_Coordinates = []

        print("Anzahl der Instanzen: " + str(current_count.counter))

        self.First_Coordinate_set = False
        self.valid_line = False

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
            "Crossed_Gates": self.Crossed_Gates,
            "Crossed_Frames": self.Crossed_Frames,
            "Crossed_Coordinates": self.Crossed_Gates_Coordinates,
        }

    def all_values_set(self):

        for key in self.counted_vehicle_information().keys():

            if (
                objectstorage.active_countings[
                    objectstorage.active_countings_index
                ].counted_vehicle_information()[key]
                is None
                or self.First_Coordinate_set is True
                or self.valid_line is False
            ):
                print(key + " is None")
                return False

        return True

    def __line_validation(self, list_of_crossed_gates):
        """Return true if line has crossed at least two sections.
        (make line valid)

        Args:
            list_of_crossed_gates (_type_): List of crossed gates

        Returns:
            _type_: _description_
        """
        if len(list_of_crossed_gates) < 2:
            return False
        print("Line is valid")
        return True

    def get_intersect_and_frame(self, event):
        """Calculates if trajectorie of vehicle crosses any section. Returns crossed Gate and Frame when crossed as list of tuples.
        Args:
            event (_type_): gets triggered when when class or coordinate is changed.
        """
        # only do when at least two points exist or at least the second point.
        if (
            objectstorage.config_dict["linedetector_toggle"]
            or not self.Exit_Coordinate
            or not objectstorage.flow_dict["Detectors"]
        ):
            return
        section_geoobjects = [
            objectstorage.flow_dict["Detectors"][k]["Geometry_line"]
            for k, v in objectstorage.flow_dict["Detectors"].items()
        ]

        section_geoseries = geopandas.GeoSeries(section_geoobjects)

        dataframe = pd.DataFrame(data=section_geoseries)
        dataframe["Detector"] = objectstorage.flow_dict["Detectors"]

        count_linestring = LineString([self.Entry_Coordinate, self.Exit_Coordinate])

        dataframe["Intersects"] = section_geoseries.intersects(count_linestring)
        dataframe["Intersects_Coord"] = section_geoseries.intersection(count_linestring)

        list_of_crossed_gates = list(
            dataframe["Detector"][dataframe["Intersects"] == True]
        )
        list_of_Crossed_Gates_Coordinates = list(
            dataframe["Intersects_Coord"][dataframe["Intersects"] == True]
        )
        # initialize empty lists
        self.Crossed_Gates = []
        self.Crossed_Frames = []
        self.Crossed_Gates_Coordinates = []

        # validate line
        self.valid_line = self.__line_validation(list_of_crossed_gates)

        if self.valid_line:

            for gate, intersection in zip(
                list_of_crossed_gates, list_of_Crossed_Gates_Coordinates
            ):

                self.Crossed_Gates.append(gate)

                self.Crossed_Gates_Coordinates.append((intersection.x, intersection.y))

            self.Entry_Gate = list_of_crossed_gates[0]
            self.Exit_Gate = list_of_crossed_gates[-1]

            if len(self.Crossed_Gates) > 2:
                self.__interpolate_frames()

    def __interpolate_frames(self):
        """Interpolates between Entry and Exit-Frame"""
        self.Crossed_Frames = [self.Entry_Frame]

        interim_result = (self.Exit_Frame - self.Entry_Frame) / (
            len(self.Crossed_Gates) - 1
        )
        if interim_result == 0:
            interim_result = 1

        for number_of_crossing_events in range(len(self.Crossed_Gates) - 2):

            self.Crossed_Frames.append(
                int((number_of_crossing_events + 1) * interim_result + self.Entry_Frame)
            )

        self.Crossed_Frames.append(self.Exit_Frame)

    def __del__(self):
        print("Object with ID " + str(self.ID) + " deleted")
