from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

VIDEO_FILE_TYPE = "mp4"
OTANALYTICS_FILE_TYPE = "otflow"
OTEVENTS_FILE_TYPE = "otevents"


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
    video_files: list[Path]
    sections_file: Path
    events_file: Path


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
            "--otflow",
            type=str,
            help="otflow file containing sections.",
            required=False,
        )
        self._parser.add_argument(
            "--otevents",
            type=str,
            help="otevents file containing events.",
            required=False,
        )

    def parse(self) -> CliArguments:
        args = self._parser.parse_args()
        video_files = self._parse_video_file_paths(files=args.videos)
        sections_file = (
            self._parse_file_path(file=args.otflow, file_type=OTANALYTICS_FILE_TYPE)
            if args.otflow is not None
            else None
        )
        events_file = (
            self._parse_file_path(file=args.otevents, file_type=OTEVENTS_FILE_TYPE)
            if args.otevents is not None
            else None
        )
        return CliArguments(
            video_files=video_files,
            sections_file=sections_file,
            events_file=events_file,
        )

    @staticmethod
    def _parse_video_file_paths(files: str) -> list[Path]:
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
                files_in_directory = video_file.rglob(f"*.{VIDEO_FILE_TYPE}")
                video_files.update(files_in_directory)
                continue

            if not video_file.exists():
                raise VideoFileDoesNotExist(f"Video file'{video_file}' does not exist.")
            if video_file.suffix != f".{VIDEO_FILE_TYPE}":
                raise InvalidVideoFileType(
                    f"Video file {video_file} has wrong file type. "
                )
            video_files.add(video_file)
        return video_files

    @staticmethod
    def _parse_file_path(file: str, file_type: str) -> Path:
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
            raise SectionsFileDoesNotExist(
                f"{file_type} file '{file_of_type}' does not exist."
            )
        if file_of_type.suffix != f".{OTANALYTICS_FILE_TYPE}":
            raise InvalidSectionFileType(
                f"{file_type} file {file_of_type} has wrong file type."
            )

        return file_of_type
