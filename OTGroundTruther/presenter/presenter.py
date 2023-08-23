from ..model.application import OTGroundTrutherApplication
from ..model.coordinate import Coordinate
from ..view.presenter_interface import PresenterInterface
from .gui_interface import Gui


class PresenterInterface:
    def __init__(self, application: OTGroundTrutherApplication, gui: Gui) -> None:
        self.application = application
        self.gui = gui

    def add_event(self, x: int, y: int) -> None:
        coordinate = Coordinate(x, y)
        event = self.application.get_event_for(coordinate)
        if event is None:
            return
        self.application.add_event_to_active_count(event)

    def update_application_property(self) -> None:
        pass

    def run(self) -> None:
        self.gui.introduce_presenter(self)
        self.gui.init_widgets()
        self.gui.place_widgets()
        self.gui.mainloop()
