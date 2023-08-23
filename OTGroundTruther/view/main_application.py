from typing import Optional, Sequence

from OTAnalytics.adapter_ui.default_values import TRACK_LENGTH_LIMIT
from OTAnalytics.application.analysis.intersect import RunIntersect
from OTAnalytics.application.analysis.traffic_counting import (
    ExportTrafficCounting,
    RoadUserAssigner,
    SimpleTaggerFactory,
)
from OTAnalytics.application.analysis.traffic_counting_specification import ExportCounts
from OTAnalytics.application.application import OTAnalyticsApplication
from OTAnalytics.application.datastore import (
    Datastore,
    EventListParser,
    FlowParser,
    TrackParser,
    TrackToVideoRepository,
)
from OTAnalytics.application.eventlist import SceneActionDetector
from OTAnalytics.application.logger import logger, setup_logger
from OTAnalytics.application.plotting import (
    LayeredPlotter,
    PlottingLayer,
    TrackBackgroundPlotter,
)
from OTAnalytics.application.state import (
    ActionState,
    FlowState,
    Plotter,
    SectionState,
    SelectedVideoUpdate,
    TrackImageUpdater,
    TrackPropertiesUpdater,
    TracksMetadata,
    TrackState,
    TrackViewState,
)
from OTAnalytics.application.use_cases.create_events import (
    CreateEvents,
    CreateIntersectionEvents,
    SimpleCreateIntersectionEvents,
    SimpleCreateSceneEvents,
)
from OTAnalytics.application.use_cases.event_repository import (
    AddEvents,
    ClearEventRepository,
)
from OTAnalytics.application.use_cases.generate_flows import (
    ArrowFlowNameGenerator,
    CrossProductFlowGenerator,
    FilterExisting,
    FilterSameSection,
    FlowIdGenerator,
    GenerateFlows,
    RepositoryFlowIdGenerator,
)
from OTAnalytics.application.use_cases.highlight_intersections import (
    TracksAssignedToSelectedFlows,
    TracksIntersectingSelectedSections,
    TracksNotIntersectingSelection,
    TracksOverlapOccurrenceWindow,
)
from OTAnalytics.application.use_cases.section_repository import AddSection
from OTAnalytics.application.use_cases.track_repository import (
    AddAllTracks,
    ClearAllTracks,
    GetAllTracks,
)
from OTAnalytics.domain.event import EventRepository, SceneEventBuilder
from OTAnalytics.domain.filter import FilterElementSettingRestorer
from OTAnalytics.domain.flow import FlowRepository
from OTAnalytics.domain.progress import ProgressbarBuilder
from OTAnalytics.domain.section import SectionRepository
from OTAnalytics.domain.track import (
    CalculateTrackClassificationByMaxConfidence,
    TrackIdProvider,
    TrackRepository,
)
from OTAnalytics.domain.video import VideoRepository
from OTAnalytics.plugin_filter.dataframe_filter import DataFrameFilterBuilder
from OTAnalytics.plugin_intersect.shapely.intersect import ShapelyIntersector
from OTAnalytics.plugin_intersect.shapely.mapping import ShapelyMapper
from OTAnalytics.plugin_intersect.simple_intersect import SimpleRunIntersect
from OTAnalytics.plugin_intersect_parallelization.multiprocessing import (
    MultiprocessingIntersectParallelization,
)
from OTAnalytics.plugin_parser.export import (
    FillZerosExporterFactory,
    SimpleExporterFactory,
)
from OTAnalytics.plugin_parser.otvision_parser import (
    CachedVideoParser,
    OtConfigParser,
    OtEventListParser,
    OtFlowParser,
    OttrkParser,
    OttrkVideoParser,
    SimpleVideoParser,
)
from OTAnalytics.plugin_progress.tqdm_progressbar import TqdmBuilder
from OTAnalytics.plugin_prototypes.eventlist_exporter.eventlist_exporter import (
    AVAILABLE_EVENTLIST_EXPORTERS,
)
from OTAnalytics.plugin_prototypes.track_visualization.track_viz import (
    CachedPandasTrackProvider,
    ColorPaletteProvider,
    FilterByClassification,
    FilterById,
    FilterByOccurrence,
    MatplotlibTrackPlotter,
    PandasDataFrameProvider,
    PandasTracksOffsetProvider,
    PlotterPrototype,
    TrackGeometryPlotter,
    TrackStartEndPointPlotter,
)
from OTAnalytics.plugin_ui.cli import (
    CliArgumentParser,
    CliArguments,
    CliParseError,
    OTAnalyticsCli,
)
from OTAnalytics.plugin_video_processing.video_reader import MoviepyVideoReader


class ApplicationStarter:
    def start(self) -> None:
        self.start_gui()

    def _build_cli_argument_parser(self) -> CliArgumentParser:
        return CliArgumentParser()

    def start_gui(self) -> None:
        # from OTAnalytics.plugin_ui.customtkinter_gui.dummy_viewmodel import (
        #     DummyViewModel,
        # )
        # from OTAnalytics.plugin_ui.customtkinter_gui.gui import (
        #     ModifiedCTk,
        #     OTAnalyticsGui,
        # )

        section_repository = self._create_section_repository()
        event_repository = self._create_event_repository()
        datastore = self._create_datastore(
            section_repository,
            event_repository,
        )

        # layers = self._create_layers(
        #     datastore,
        #     track_view_state,
        #     flow_state,
        #     section_state,
        #     pandas_data_provider,
        #     road_user_assigner,
        #     color_palette_provider,
        # )
        # plotter = LayeredPlotter(layers=layers)
        image_updater = TrackImageUpdater(datastore, plotter)

        selected_video_updater = SelectedVideoUpdate(datastore, track_view_state)

        add_events = AddEvents(event_repository)
        create_events = self._create_use_case_create_events(
            section_repository, event_repository, add_events
        )

        application = OTAnalyticsApplication(
            datastore=datastore,
            create_events=create_events,
        )
        application.connect_clear_event_repository_observer()
        flow_parser: FlowParser = application._datastore._flow_parser
        name_generator = ArrowFlowNameGenerator()
        dummy_viewmodel = DummyViewModel(
            application,
            flow_parser,
            name_generator,
            event_list_export_formats=AVAILABLE_EVENTLIST_EXPORTERS,
        )

        main_window = ModifiedCTk(dummy_viewmodel)
        OTAnalyticsGui(main_window, dummy_viewmodel, layers).start()

    def _create_datastore(
        self,
        track_repository: TrackRepository,
        section_repository: SectionRepository,
        flow_repository: FlowRepository,
        event_repository: EventRepository,
        progressbar_builder: ProgressbarBuilder,
    ) -> Datastore:
        """
        Build all required objects and inject them where necessary

        Args:
            track_repository (TrackRepository): the track repository to inject
            progressbar_builder (ProgressbarBuilder): the progressbar builder to inject
        """
        track_parser = self._create_track_parser(track_repository)
        flow_parser = self._create_flow_parser()
        event_list_parser = self._create_event_list_parser()
        video_parser = CachedVideoParser(SimpleVideoParser(MoviepyVideoReader()))
        video_repository = VideoRepository()
        track_to_video_repository = TrackToVideoRepository()
        track_video_parser = OttrkVideoParser(video_parser)
        config_parser = OtConfigParser(
            video_parser=video_parser,
            flow_parser=flow_parser,
        )
        return Datastore(
            track_repository,
            track_parser,
            section_repository,
            flow_parser,
            flow_repository,
            event_repository,
            event_list_parser,
            track_to_video_repository,
            video_repository,
            video_parser,
            track_video_parser,
            progressbar_builder,
            config_parser=config_parser,
        )

    def _create_section_repository(self) -> SectionRepository:
        return SectionRepository()

    def _create_flow_parser(self) -> FlowParser:
        return OtFlowParser()

    def _create_event_repository(self) -> EventRepository:
        return EventRepository()

    def _create_event_list_parser(self) -> EventListParser:
        return OtEventListParser()

    def _create_layers(
        self,
        datastore: Datastore,
        track_view_state: TrackViewState,
        flow_state: FlowState,
        section_state: SectionState,
        pandas_data_provider: PandasDataFrameProvider,
        road_user_assigner: RoadUserAssigner,
        color_palette_provider: ColorPaletteProvider,
    ) -> Sequence[PlottingLayer]:
        background_image_plotter = TrackBackgroundPlotter(track_view_state, datastore)
        background_layer = PlottingLayer("Background", background_image_plotter, enabled=True)
        
 

        return [
            background_layer,
            sections_layer
            counts_layer,
        ]

    def _create_use_case_create_events(
        self,
        section_repository: SectionRepository,
        event_repository: EventRepository,
        get_all_tracks: GetAllTracks,
        add_events: AddEvents,
    ) -> CreateEvents:
        run_intersect = self._create_intersect(get_all_tracks)
        clear_event_repository = ClearEventRepository(event_repository)
        create_intersection_events = SimpleCreateIntersectionEvents(
            run_intersect, section_repository, add_events
        )
        scene_action_detector = SceneActionDetector(SceneEventBuilder())
        create_scene_events = SimpleCreateSceneEvents(
            get_all_tracks, scene_action_detector, add_events
        )
        return CreateEvents(
            clear_event_repository, create_intersection_events, create_scene_events
        )
