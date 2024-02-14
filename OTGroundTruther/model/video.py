import datetime as dt
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import cv2
import numpy.typing as npt
from PIL import Image


class NoVideoError(Exception):
    pass


def _get_datetime_from_filename(
    filename: str, epoch_datetime: str = "1970-01-01_00-00-00"
) -> tuple[float, str]:
    """Get date and time from file name.
    Searches for "_yyyy-mm-dd_hh-mm-ss".
    Returns timestamp in seconds since epoch and "yyyy-mm-dd_hh-mm-ss".

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
        return 0, epoch_datetime

    datetime = match[1]

    try:
        seconds_since_epoch = dt.datetime.strptime(
            datetime, "%Y-%m-%d_%H-%M-%S"
        ).timestamp()
    except ValueError:
        return 0, epoch_datetime

    return seconds_since_epoch, datetime


class NumberOfFramesUnknownError(Exception):
    pass


class FrameNotFoundInVideoError(Exception):
    pass


class VideoNotFoundError(Exception):
    pass


class TimestampNotFoundInVideosError(Exception):
    pass


@dataclass
class BackgroundFrame:
    np_array: npt.NDArray
    video_file: Path
    frame_number: int
    unix_timestamp: float
    image: Image.Image = field(init=False)

    def __post_init__(self):
        self.image = Image.fromarray(cv2.cvtColor(self.np_array, cv2.COLOR_BGR2RGB))

    def get_width(self) -> int:
        return self.np_array.shape[1]

    def get_height(self) -> int:
        return self.np_array.shape[0]

    def get(self) -> Image.Image:
        return self.image

    def get_unix_timestamp(self) -> float:
        return self.unix_timestamp

    def add_overlay(self, overlay: Image.Image) -> None:
        self.image = Image.alpha_composite(
            self.image.convert("RGBA"), overlay.convert(mode="RGBA")
        )

    def get_frame_number(self) -> int:
        return self.frame_number

    def get_video_file(self) -> Path:
        return self.video_file

    def get_video_name(self) -> str:
        return self.video_file.name


class Video:
    def __init__(self, file: Path):
        self.file: Path = file
        self._load()
        self._set_frame_rate()
        self._set_number_of_frames()
        self._start_timestamp, self._start_datetime = self._parse_start_time()

    def _load(self):
        self.cap = cv2.VideoCapture(str(self.file))
        if not self._is_loaded():
            raise ValueError(f"Konnte das Video {self.file} nicht öffnen.")

    def _is_loaded(self) -> bool:
        return self.cap.isOpened()

    def get_width(self) -> int:
        return self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)

    def get_height(self) -> int:
        return self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    def get_filepath(self) -> Path:
        return self.file

    def get_name(self) -> str:
        return self.file.name

    def get_frame_rate(self) -> float:
        return self.frame_rate

    def _set_frame_rate(self) -> None:
        self.frame_rate = self.cap.get(cv2.CAP_PROP_FPS)

    def _set_number_of_frames(self) -> None:
        calculated_frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        for frame_number in range(
            calculated_frame_count - 3, calculated_frame_count + 3
        ):
            try:
                self._get_frame_by_number(frame_number=frame_number)
            except FrameNotFoundInVideoError:
                self.number_of_frames = frame_number
                if frame_number == calculated_frame_count - 3:
                    raise NumberOfFramesUnknownError
                else:
                    break
            else:
                pass

    def _parse_start_time(self) -> tuple[float, str]:
        return _get_datetime_from_filename(filename=str(self.file))

    def get_start_timestamp(self) -> float:
        return self._start_timestamp

    def get_start_datetime(self) -> str:
        return self._start_datetime

    def get_number_of_frames(self):
        return self.number_of_frames

    def get_duration_in_seconds(self) -> float:
        return self.get_number_of_frames / self.frame_rate

    def set_frame_number(self, frame_number: int) -> None:
        self.cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

    def get_frame_by_number(self, frame_number: int) -> "BackgroundFrame":
        frame = self._get_frame_by_number(frame_number)
        unix_timestamp = self.get_timestamp_by_frame_number(frame_number)
        return BackgroundFrame(
            np_array=frame,
            frame_number=frame_number,
            unix_timestamp=unix_timestamp,
            video_file=self.file,
        )

    def get_frame_by_timestamp(self, unix_timestamp: float) -> "BackgroundFrame":
        frame_number = self.get_frame_number_by_timestamp(unix_timestamp)
        if frame_number <= 0 or frame_number > self.get_number_of_frames():
            raise ValueError("frame_number is not in video")
        return self.get_frame_by_number(frame_number)

    def _get_frame_by_number(self, frame_number: int) -> npt.NDArray:
        if frame_number == self._get_current_frame_number() + 1:
            pass
        elif frame_number == 0:
            self.cap.release()
            self._load()
        else:
            self.set_frame_number(frame_number - 1)
        ret, frame = self.cap.read()
        if not ret:
            raise FrameNotFoundInVideoError()
        return frame

    def _get_current_frame_number(self) -> int:
        return self.cap.get(cv2.CAP_PROP_POS_FRAMES)

    def get_timestamp_by_frame_number(self, frame_number: int) -> float:
        return self._start_timestamp + frame_number / self.frame_rate

    def get_frame_number_by_timestamp(self, unix_timestamp: float) -> int:
        if not self.includes_timestamp(unix_timestamp):
            raise FrameNotFoundInVideoError()
        return int(
            round(((unix_timestamp - self._start_timestamp) * self.frame_rate), 0)
        )

    def get_time_period(self) -> tuple[float, float]:
        return (
            self._start_timestamp,
            self._start_timestamp + self.get_duration_in_seconds(),
        )

    def includes_timestamp(self, unix_timestamp: float) -> bool:
        start, end = self.get_time_period()
        return start <= unix_timestamp <= end

    def __del__(self):
        if self.cap:
            self.cap.release()


class VideoRepository:
    def __init__(self) -> None:
        self._videos: dict[str, Video] = {}

    def add(self, video: Video) -> None:
        """Add one video to the repository.

        Args:
            video (Video): the video to add
        """
        self._add(video)

    def add_all(self, videos: Iterable[Video]) -> None:
        """Add several videos at once to the repository.

        Args:
            videos (Iterable[Video]): the videos to add
        """
        for video in videos:
            self._add(video)

    def _add(self, video: Video) -> None:
        """Internal method to add a video.

        Args:
            video (Video): the video to be added
        """
        self._videos[video.get_name()] = video

    def get_by_timestamp(self, unix_timestamp: float) -> Video | None:
        for video in self._videos.values():
            if video.includes_timestamp(unix_timestamp):
                return video
        return None

    def get_video_and_frame_by_delta_frame_or_time(
        self,
        current_file_name: str,
        current_frame_number: int,
        delta_of_frames: int = 0,
        delta_of_time: float = 0,
    ) -> tuple[Video, int]:
        current_video = self.get_video_by_name(file_name=current_file_name)
        delta_of_frames += round(delta_of_time * current_video.get_frame_rate())
        return self.get_video_and_frame_by_delta_frame(
            current_file_name=current_file_name,
            current_frame_number=current_frame_number,
            delta_of_frames=delta_of_frames,
        )

    def get_video_and_frame_by_delta_frame(
        self,
        current_file_name: str,
        current_frame_number: int,
        delta_of_frames: int = 0,
    ) -> tuple[Video, int]:
        current_video = self.get_video_by_name(file_name=current_file_name)

        new_frame_number = current_frame_number + delta_of_frames
        current_video_number_of_frames = current_video.get_number_of_frames()

        if 0 <= new_frame_number < current_video_number_of_frames:
            return current_video, new_frame_number

        if new_frame_number < 0:
            return self._try_get_by_delta_from_previous(
                current_video=current_video,
                current_frame_number=current_frame_number,
                delta_of_frames=delta_of_frames,
            )
        else:
            return self._try_get_by_delta_from_next(
                current_video=current_video,
                current_frame_number=current_frame_number,
                delta_of_frames=delta_of_frames,
            )

    def _try_get_by_delta_from_next(
        self, current_video: Video, current_frame_number: int, delta_of_frames: int
    ):
        if self.is_last_video(current_video):
            return current_video, current_video.get_number_of_frames() - 1
        current_video_index = self._get_index_by_video(current_video)
        new_video_index = current_video_index + 1
        new_video = self._get_video_by_index(new_video_index)
        new_delta_of_frames = delta_of_frames - (
            current_video.get_number_of_frames() - current_frame_number
        )
        return self.get_video_and_frame_by_delta_frame(
            current_file_name=new_video.get_name(),
            current_frame_number=0,
            delta_of_frames=new_delta_of_frames,
        )

    def _try_get_by_delta_from_previous(
        self, current_video: Video, current_frame_number: int, delta_of_frames: int
    ):
        current_video_index = self._get_index_by_video(current_video)
        new_video_index = current_video_index - 1
        if new_video_index < 0:
            return self._get_video_by_index(current_video_index), 0
        new_video = self._get_video_by_index(new_video_index)
        new_delta_of_frames = delta_of_frames + current_frame_number
        return self.get_video_and_frame_by_delta_frame(
            current_file_name=new_video.get_name(),
            current_frame_number=new_video.get_number_of_frames(),
            delta_of_frames=new_delta_of_frames,
        )

    def is_last_video(self, current_video: Video) -> bool:
        current_video_index = self._get_index_by_video(current_video)
        new_video_index = current_video_index + 1
        return new_video_index > len(self._videos) - 1

    def _get_video_by_index(self, index: int) -> Video:
        return list(self._videos.values())[index]

    def _get_index_by_file_name(self, file_name: str) -> int:
        return list(self._videos.keys()).index(file_name)

    def _get_index_by_video(self, video: Video) -> int:
        return list(self._videos.values()).index(video)

    def get_video_by_name(self, file_name: str) -> Video:
        return self._videos[file_name]

    def get_first_video(self) -> Video:
        return list(self._videos.values())[0]

    def is_empty(self) -> bool:
        return not self._videos

    def clear(self):
        self._videos.clear()
