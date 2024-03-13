from __future__ import annotations
import collections
import fnmatch
import math
import os
from typing import Any, Dict, List, Tuple

from PIL import Image


class LightmapCollection:
    """for organising named lightmaps (e.g. titanfall SKY & RTL)"""
    name: str
    _lightmaps: Dict[Any, Image]
    # ^ {0: ..., ("LDR", 0): ..., "named": ...}

    # TODO: int & slice indexing
    # TODO: (str, int) tuple keys
    # -- lock in padding for each "group"
    # -- groups are names with the same length, strings & string order

    def __init__(self, name: str, **kwargs: Dict[str, Image]):
        self.name = name
        self._lightmaps = kwargs.copy()

    def __repr__(self) -> str:
        num_lightmaps = f"{len(self)} lightmaps"
        return f"<LightmapCollection {self.name!r} {num_lightmaps} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        return len(self._lightmaps)

    def __getitem__(self, key: Any) -> Image:
        return self._lightmaps[key]

    def __setitem__(self, key: Any, image: Image):
        self._lightmaps[key] = image

    @classmethod
    def from_list(cls, name: str, lightmaps: List[Image]) -> LightmapCollection:
        assert isinstance(name, str), "LightmapCollection must have a name!"
        return cls(name, **dict(enumerate(lightmaps)))

    def matches(self, pattern: str) -> List[str]:
        return fnmatch.filter(self.namelist(), pattern)

    def namelist(self) -> List[str]:
        return sorted(self._lightmaps.keys())

    def save_all(self, folder: str = "./", extension: str = ".tga"):
        # TODO: tests
        os.makedirs(folder, exist_ok=True)
        # filename preprocessing
        # TODO: include unique strings in spec
        # TODO: only do spec classification on tuple keys
        # specs_by_key = {
        #     key: tuple([i for i, k in enumerate(key) if isinstance(k, int)])
        #     for key in self._lightmaps.keys()}
        # keys_by_spec = collections.defaultdict(set)
        # for key, spec in specs_by_key.items():
        #     keys_by_spec[spec].add(key)
        # pad_lengths = {
        #     spec: {i: max([key[i] for key in keys]) for i in spec}
        #     for spec, keys in keys_by_spec.items()}
        # filenames = {
        #     key: ".".join([
        #         f"{k:0{pad[i]}d}" if i in pad else str(k)
        #         for i, k in enumerate(key)])
        #     for spec, pad in pad_lengths.items()
        #     for key in keys_by_spec[spec]}
        for key, image in self._lightmaps.items():
            # filename = filenames[key]
            if isinstance(key, (str, int)):
                filename = str(key)
            elif isinstance(key, tuple):
                assert all(isinstance(k, (str, int)) for k in key)
                # TODO: padding by key spec
                filename = ".".join(map(str, key))
            else:
                raise KeyError(f"couldn't convert key to filename: {key}")
            image.save(os.path.join(folder, f"{self.name}.{filename}.{extension}"))


# LightmapPage utils
AllocatedSpace = collections.namedtuple("AllocatedSpace", ["x", "y", "width", "height"])
Row = collections.namedtuple("Row", ["top", "height", "free_width"])


class LightmapPage:
    """for grouping small per-face lightmaps"""
    children: Dict[AllocatedSpace, Image.Image]
    colour_mode: str
    rows: List[Row]
    # properties
    child_bounds: List[Dict[Tuple[int, int]]]
    # ^ [{"mins": [x, y], "maxs": [x, y]}]
    image: Image.Image

    # TODO: pack w/ bleed margins
    # -- pre-bleed each image before adding it?
    # TODO: pack "styles" in series & use a `lightmap_step` UV
    # -- would have to pre-group styles for a given face into one image (with another LightmapPage?)

    def __init__(self, max_width=1024, max_height=math.inf, colour_mode="RGBA"):
        self.max_width, self.max_height = max_width, max_height
        self.colour_mode = colour_mode
        self.rows = [Row(0, max_height, max_width)]
        self.children = dict()

    def __repr__(self) -> str:
        dimensions = f"{self.max_width}x{self.max_height}px"
        num_lightmaps = f"{len(self)} lightmaps"
        return f"<LightmapPage {self.colour_mode} {dimensions} {num_lightmaps} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        return len(self.children)

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

    @classmethod
    def from_list(cls, lightmaps: List[Image], max_width=1024) -> LightmapPage:
        # TODO: sort lightmaps for more efficient pack, but retain child order
        # -- we'll need this for remapping uvs
        # size_order = sorted(
        #     [i for i, lightmap in enumerate(lightmaps)],
        #     key=lambda i: (-lightmaps[i].size[0], -lightmaps[i].size[1]))
        # page = sum([images[i] for i in size_order], start=cls(max_width=max_width))
        # # TODO: OrderedDict assemble new children in lightmaps order
        # lut = [size_order.index(i) for i, _ in enumerate(lightmaps)]
        # children = list(page.children.items())  # indexable copy
        # page.children = {k: v for k, v in [children[i] for i in lut]}
        return sum(lightmaps, start=cls(max_width=max_width))

    @classmethod
    def from_collection(cls, collection: LightmapCollection, pattern: str = "*") -> LightmapPage:
        # TODO: retain a map of collection name -> AllocatedSpace
        # -- saves us from doing the cursed mess in .from_list()
        return cls.from_list([collection[name] for name in collection.matches(pattern)])

    @property
    def child_bounds(self):
        """.json-friendly"""
        return [{"mins": [c.x, c.y], "maxs": [c.x + c.width, c.y + c.height]} for c in self.children]

    @property
    def image(self):
        """Composite final image"""
        if len(self) == 0:
            return None  # empty
        width = max([x + w for x, y, w, h in self.children])
        height = max([y + h for x, y, w, h in self.children])
        page = Image.new(self.colour_mode, (width, height))
        for space, child in self.children.items():
            x, y, width, height = space
            page.paste(child, (x, y, x + width, y + height))
        return page

    def save_as(self, filename: str):
        folder = os.path.split(filename)[0]
        os.makedirs(folder, exist_ok=True)
        self.image.save(filename)
