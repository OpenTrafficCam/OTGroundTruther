from model.application import OTGroundTrutherApplication


class ViewModel:
    def __init__(
        self,
        application: OTGroundTrutherApplication,
        event_list_export_formats: dict,
    ) -> None:
        self._application = application
        self._event_list_export_formats = event_list_export_formats
