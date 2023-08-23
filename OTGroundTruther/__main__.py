from model.application import OTGroundTrutherApplication
from presenter.presenter import Presenter

from view.gui import Gui


def main() -> None:
    application = OTGroundTrutherApplication()
    gui = Gui()
    presenter = Presenter(application, gui)
    presenter.run()


if __name__ == "__main__":
    main()
