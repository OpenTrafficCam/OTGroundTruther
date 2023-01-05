import pandas as pd
import time

maincanvas = None
videoobject = None
sliderobject = None


# list with active counts
active_countings = []
active_countings_index = 0

# ground_truth = []
ground_truth = pd.DataFrame(
     columns=[
        "ID", "Class",
            "Crossed_Gates",
            "Crossed_Frames",
            "Crossed_Coordinates",
        ]

)
starttime = time.time()
eventbased_dictionary = {}
eventbased_dictionary_index = 0

background_dic = {}

use_test_version = "Test"
quicksafe_filepath_event = None

flow_dict = {"Detectors": {}, "Movements": {}}

config_dict = {
    "linedetector_toggle": False,
    "polygondetector_toggle": False,
    "tracks_imported": False,
    "detections_drawn": False,
    "display_all_tracks_toggle": False,
    "play_video": False,
    "rewind_video": False,
    "counting_mode": False,
    "during_counting_process": False,
    "mousescroll_active": False,
    "display_bb": False,
    "display_live_track": False,
    "slider": False,
    "dataframe_cleaned": False,
    "gt_active": True,
    "count_active": False,
}


color_dict = {
    "car": (89, 101, 212),
    "bicycle": (73, 166, 91),
    "truck": (97, 198, 212),
    "motorcycle": (148, 52, 137),
    "person": (214, 107, 88),
    "bus": (179, 177, 68),
}
#TODO: Implement ELLIPSEHEIGHT
ELLIPSEHEIGHT = 0.15
"Factor that gets multiplied with ellipsewidth to define ellipseheihgt"

MAXSCROLLSPEED = 40
"Maxscrollspeed"
