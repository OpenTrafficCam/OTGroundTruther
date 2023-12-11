import copy
from dataclasses import dataclass

from PIL import Image

from OTGroundTruther.model.count import CountsOverlay
from OTGroundTruther.model.section import SectionsOverlay
from OTGroundTruther.model.video import BackgroundFrame


@dataclass
class OverlayedFrame:
    background_frame: BackgroundFrame
    sections_overlay: SectionsOverlay
    counts_overlay: CountsOverlay

    def get(
        self, overlay_sections: bool = True, overlay_counts: bool = True
    ) -> Image.Image:
        image = copy.deepcopy(self.background_frame)
        if overlay_sections:
            image.add_overlay(overlay=self.sections_overlay.get())
        if overlay_counts:
            image.add_overlay(overlay=self.counts_overlay.get())
        return image.get()
