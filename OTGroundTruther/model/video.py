import datetime as dt
import re
from pathlib import Path

import cv2
import numpy as np


class NoVideoError(Exception):
    pass


def _get_datetime_from_filename(
    filename: str, epoch_datetime: str = "1970-01-01_00-00-00"
) -> tuple[float, str]:
    """Get date and time from file name.
    Searches for "_yyyy-mm-dd_hh-mm-ss".
    Returns "yyyy-mm-dd_hh-mm-ss".

    Args:
        filename (str): filename with expression
        epoch_datetime (str): Unix epoch (00:00:00 on 1 January 1970)

    Returns:
        float: seconds since epoch
        str: datetime
    """
    regex = "_([0-9]{4,4}-[0-9]{2,2}-[0-9]{2,2}_[0-9]{2,2}-[0-9]{2,2}-[0-9]{2,2})"
    match = re.search(regex, filename)
    if not match:
        return epoch_datetime

    # Assume that there is only one timestamp in the file name
    datetime = match[1]

    try:
        seconds_since_epoch = dt.datetime.strptime(
            datetime, "%Y-%m-%d_%H-%M-%S"
        ).timestamp()
    except ValueError:
        return 0, epoch_datetime

    return seconds_since_epoch, datetime


class FrameNotFoundInVideoError(Exception):
    pass


class VideoObject:
    def __init__(self, file: str):
        self.video_path = file
        self.cap: cv2.VideoCapture | None = None
        self.frame_count: int | None = None

    def load(self):
        self.cap = cv2.VideoCapture(self.video_path)
        if not self.cap.isOpened():
            raise ValueError(f"Konnte das Video {self.video_path} nicht öffnen.")
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_frame(self, frame_number: int) -> tuple[int, int, int]:
        if not self.cap.isOpened():
            raise ValueError(
                "Das Video wurde nicht geladen. Bitte rufe zuerst die 'load' Methode auf."
            )

        if frame_number < 0 or frame_number >= self.frame_count:
            raise FrameNotFoundInVideoError(
                f"Frame {frame_number} nicht im Video gefunden."
            )

        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
        ret, frame = self.cap.read()

        if not ret:
            raise FrameNotFoundInVideoError(
                f"Fehler beim Abrufen von Frame {frame_number}."
            )

        return frame


class Video:
    def __init__(self, file: Path):
        self.file: Path
        self._load()
        self._set_frame_rate()
        self._parse_start_time()

    def _load(self):
        self.cap = cv2.VideoCapture(self.file)
        if not self._is_loaded():
            raise ValueError(f"Konnte das Video {self.file} nicht öffnen.")

    def _is_loaded(self) -> bool:
        return self.cap.isOpened()

    def _set_frame_rate(self) -> float:
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

    def _parse_start_time(self) -> None:
        self.start_timestamp, self.start_datetime = _get_datetime_from_filename(
            filename=str(self.file)
        )

    def get_start_timestamp(self) -> float:
        return self.start_timestamp

    def get_start_datetime(self) -> str:
        return self.start_datetime

    def get_total_number_of_frames(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def get_video_length_in_seconds(self) -> float:
        return

    def get_frame_number(self) -> int:
        self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    def set_frame_number(self, frame_number: int) -> None:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def get_frame(self) -> np.array:
        ret, frame = self.cap.read()
        if not ret:
            raise FrameNotFoundInVideoError()
        return frame

    def get_timestamp(self) -> float:
        frame_number = self.get_frame_number
        return self.start_timestamp + frame_number / self.frame_rate

    def __del__(self):
        if self.cap:
            self.cap.release()
