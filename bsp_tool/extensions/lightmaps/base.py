import collections
import math
from typing import Dict, List

from PIL import Image  # requires: pip install Pillow


# TODO: pack w/ bleed margins
# TODO: pack styles in series & use a `lightmap_step` UV
# TODO: page children as .json

AllocatedSpace = collections.namedtuple("AllocatedSpace", ["x", "y", "width", "height"])
Row = collections.namedtuple("Row", ["top", "height", "free_width"])


class LightmapPage:
    """Packs smaller images into a larger one"""
    children: Dict[AllocatedSpace, Image.Image]
    # NOTE: list(chilren.keys()) is a decent .json reference
    colour_mode: str
    image: Image.Image
    rows: List[Row]

    def __init__(self, max_width=1024, max_height=math.inf, colour_mode="RGBA"):
        self.max_width, self.max_height = max_width, max_height
        self.colour_mode = colour_mode
        self.rows = [Row(0, max_height, max_width)]
        self.children = dict()  # create a new dict! must be clean!

    def __add__(self, image: Image.Image):  # mutates self
        """Works best if images are sorted beforehand"""
        width, height = image.size
        if width > self.max_width:
            raise RuntimeError(f"{image!r} is too wide for {self!r}!")
        # try and fit image into a row
        i, allocated = 0, False
        while not allocated and i < len(self.rows):
            row = self.rows[i]
            if row.free_width == self.max_width:  # row is empty
                x, y = 0, row.top
                new_row_height = height
                sliced_row = Row(row.top + height, row.height - height, self.max_width)
                if sliced_row.height > 0:
                    self.rows.append(sliced_row)
                allocated = True
            elif row.free_width >= width and row.height >= height:  # will fit
                x, y = (self.max_width - row.free_width), row.top
                new_row_height = row.height
                allocated = True
            i += 1
        if not allocated:
            raise RuntimeError(f"No space left in {self!r}!")
        # update the row allocated to
        new_row = Row(row.top, new_row_height, row.free_width - width)
        self.rows[i - 1] = new_row
        if row.free_width == 0:
            self.rows.pop(i)
        self.children[AllocatedSpace(x, y, width, height)] = image
        return self

    @property
    def image(self):
        """Composite final image"""
        if len(self.children) == 0:
            return None  # empty
        width = max([x + w for x, y, w, h in self.children])
        height = max([y + h for x, y, w, h in self.children])
        page = Image.new(self.colour_mode, (width, height))
        for space, child in self.children.items():
            x, y, width, height = space
            page.paste(child, (x, y, x + width, y + height))
        return page


def pack(images: List[Image], max_width=1024) -> Image:
    return sum(images, start=LightmapPage(max_width=max_width)).image
