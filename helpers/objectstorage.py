import pandas as pd

maincanvas = None
videoobject = None
sliderobject = None

# list with active counts
active_countings = []
active_countings_index = 0

# ground_truth = []
ground_truth = pd.DataFrame(
    columns=[
        "ID",
        "Class",
        "Entry_Gate",
        "Entry_Frame",
        "Entry_Coordinate",
        "Exit_Gate",
        "Exit_Frame",
        "Exit_Coordinate",
    ]
)
background_dic = {}

flow_dict = {"Detectors": {}, "Movements": {}}

button_bool = {
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
    "gt_line": False,
    "gt_polyline": True,
}


color_dict = {
    "car": (89, 101, 212),
    "bicycle": (73, 166, 91),
    "truck": (97, 198, 212),
    "motorcycle": (148, 52, 137),
    "person": (214, 107, 88),
    "bus": (179, 177, 68),
}