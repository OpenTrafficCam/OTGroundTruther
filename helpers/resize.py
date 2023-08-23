import helpers.filehelper.objectstorage as objectstorage


def get_canvas_coordinate_for(video_coordinate):
    return (
        int(video_coordinate[0] * objectstorage.videoobject.x_resize_factor),
        int(video_coordinate[1] * objectstorage.videoobject.y_resize_factor),
    )
