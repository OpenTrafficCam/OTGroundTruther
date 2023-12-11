from abc import ABC, abstractmethod


class PresenterInterface(ABC):
    @abstractmethod
    def after_run_gui(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_video_files(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_otflow(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def load_events(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def save_events(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def scroll_through_videos(
        self, scroll_delta: int, mouse_wheel_pressed: bool
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def try_add_event(self, x: int, y: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def set_road_user_class_for_active_count(self, key: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def finsh_active_count(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def abort_active_count(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def jump_by_delta_time_in_sec(self, delta_of_time: float) -> None:
        raise NotImplementedError

    @abstractmethod
    def refresh_treeview(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def delete_selected_counts(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_start_of_count(self, count_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def update_canvas_image_with_new_overlay(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_selected_classes_from_gui(self) -> list[str]:
        raise NotImplementedError

    @abstractmethod
    def show_class_image_by_count_id(self, count_id: int) -> None:
        raise NotImplementedError

    @abstractmethod
    def show_key_assignment(self) -> None:
        raise NotImplementedError
