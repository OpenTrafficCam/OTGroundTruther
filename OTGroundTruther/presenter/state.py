from dataclasses import dataclass


@dataclass
class DisplayedFrameState:
    _video_id: str | None
    _unix_timestamp: float | None

    def get_video_id(self) -> str | None:
        return self._video_id

    def get_timestamp(self) -> float | None:
        return self._unix_timestamp

    def _set_video_id(self, video_id: str) -> None:
        self._video_id = video_id

    def _set_timestamp(self, unix_timestamp: float) -> None:
        self._unix_timestamp = unix_timestamp

    def set(self, video_id: str, unix_timestamp: float):
        self._set_video_id(video_id)
        self._set_timestamp(unix_timestamp)
