from OTGroundTruther.presenter.model_initializer import ModelInitializer
from OTGroundTruther.presenter.presenter import Presenter


def main() -> None:
    model = ModelInitializer().get()
    presenter = Presenter(model=model)
    presenter.run_gui()


if __name__ == "__main__":
    main()
