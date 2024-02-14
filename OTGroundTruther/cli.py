from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from OTGroundTruther.model.config import (
    DEFAULT_VIDEO_FILE_SUFFIX,
    GROUND_TRUTH_EVENTS_FILE_SUFFIX,
    OTANALYTICS_FILE_SUFFIX,
    OTEVENTS_FILE_SUFFIX,
)


class SectionsFileDoesNotExist(Exception):
    pass


class InvalidSectionFileType(Exception):
    pass


class VideoFileDoesNotExist(Exception):
    pass


class InvalidVideoFileType(Exception):
    pass


@dataclass(frozen=True)
class CliArguments:
    video_files: set[Path]
    sections_file: Path | None
    events_file: Path | None


class CliArgumentParser:
    """OTGroundTruther command line interface argument parser.

    Acts as a wrapper to `argparse.ArgumentParser`.

    Args:
        arg_parser (ArgumentParser, optional): the argument parser.
            Defaults to ArgumentParser("OTGroundTruther CLI").
    """

    def __init__(
        self, arg_parser: ArgumentParser = ArgumentParser("OTGroundTruther CLI")
    ) -> None:
        self._parser = arg_parser
        self._setup()

    def _setup(self) -> None:
        """Sets up the argument parser by defining the command line arguments."""
        self._parser.add_argument(
            "--videos",
            nargs="+",
            type=str,
            help="Paths of video files.",
            required=False,
        )
        self._parser.add_argument(
            "--sections",
            type=str,
            help=f"{OTANALYTICS_FILE_SUFFIX} file containing sections.",
            required=False,
        )
        self._parser.add_argument(
            "--events",
            type=str,
            help=f"{GROUND_TRUTH_EVENTS_FILE_SUFFIX} or {OTEVENTS_FILE_SUFFIX} file"
            "containing sections and events.",
            required=False,
        )

    def parse(self) -> CliArguments:
        args = self._parser.parse_args()
        if args.videos is None:
            video_files: set[Path] = set()
        else:
            video_files = self._parse_video_file_paths(files=args.videos)
        sections_file = (
            self._parse_file_path(
                file=args.sections, file_types=[OTANALYTICS_FILE_SUFFIX]
            )
            if args.sections is not None
            else None
        )
        events_file = (
            self._parse_file_path(
                file=args.events,
                file_types=[GROUND_TRUTH_EVENTS_FILE_SUFFIX, OTEVENTS_FILE_SUFFIX],
            )
            if args.events is not None
            else None
        )
        return CliArguments(
            video_files=video_files,
            sections_file=sections_file,
            events_file=events_file,
        )

    @staticmethod
    def _parse_video_file_paths(files: str) -> set[Path]:
        """Parse video files.

        Files that do not exist will be skipped.

        Args:
            files (list[str]): video files to be parsed

        Raises:
            VideoFileDoesNotExist: if video file does not exist
            InvalidVideoFileType: if file has invalid type

        Returns:
            list[Path]: the video files.
        """
        video_files: set[Path] = set()
        for file in files:
            video_file = Path(file)
            if video_file.is_dir():
                files_in_directory = video_file.rglob(f"*{DEFAULT_VIDEO_FILE_SUFFIX}")
                video_files.update(files_in_directory)
                continue

            if not video_file.exists():
                raise VideoFileDoesNotExist(f"Video file'{video_file}' does not exist.")
            if video_file.suffix != f"{DEFAULT_VIDEO_FILE_SUFFIX}":
                raise InvalidVideoFileType(
                    f"Video file {video_file} has wrong file type. "
                )
            video_files.add(video_file)
        return video_files

    @staticmethod
    def _parse_file_path(file: str, file_types: list[str]) -> Path:
        """Parse file of specific type.

        Args:
            file (str): the sections file to be parsed

        Raises:
            SectionFileDoesNotExist: if sections file does not exist
            InvalidSectionsFileType: if file has invalid type

        Returns:
            Path: the sections file.
        """
        file_of_type = Path(file)
        if not file_of_type.exists():
            raise SectionsFileDoesNotExist(f"'{file_of_type}' does not exist.")
        if file_of_type.suffix not in [f"{file_type}" for file_type in file_types]:
            raise InvalidSectionFileType(
                f"'{file_of_type}' has wrong file type, has to be one of {file_types}."
            )

        return file_of_type
