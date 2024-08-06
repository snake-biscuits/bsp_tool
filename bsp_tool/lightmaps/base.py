from __future__ import annotations
import collections
import fnmatch
import math
import os
from typing import Any, Dict, List, Tuple, Union

from PIL import Image


LightmapID = Union[str, Tuple[str, int]]
# e.g. "SKY.A.0" or ("SKY", "A", 0)
# use LightmapCollection.subset("SKY.A.*") to filter


class LightmapCollection:
    """for organising named lightmaps (e.g. titanfall SKY & RTL)"""
    name: str
    _lightmaps: Dict[LightmapID, Image]
    # ^ {0: ..., ("LDR", 0): ..., "named": ...}

    # TODO: int & slice indexing
    # TODO: (str, int) tuple keys
    # -- lock in padding for each "group"
    # -- groups are names with the same length, strings & string order

    def __init__(self, name: str, **kwargs: Dict[str, Image]):
        self.name = name
        self._lightmaps = {
            tuple((int(k) if k.isnumeric() else k) for k in key.split(".")): value
            for key, value in kwargs.items()}

    def __iter__(self):
        return iter(self.namelist())

    def __repr__(self) -> str:
        num_lightmaps = f"{len(self)} lightmaps"
        return f"<LightmapCollection {self.name!r} {num_lightmaps} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        return len(self._lightmaps)

    def __delitem__(self, key: Any) -> Image:
        if isinstance(key, str):
            key = tuple((int(k) if k.isnumeric() else k) for k in key.split("."))
        del self._lightmaps[key]

    def __getitem__(self, key: Any) -> Image:
        if isinstance(key, str):
            key = tuple((int(k) if k.isnumeric() else k) for k in key.split("."))
        return self._lightmaps[key]

    def __setitem__(self, key: Any, image: Image):
        if isinstance(key, str):
            key = tuple((int(k) if k.isnumeric() else k) for k in key.split("."))
        self._lightmaps[key] = image

    @classmethod
    def from_list(cls, name: str, lightmaps: List[Image]) -> LightmapCollection:
        assert isinstance(name, str), "LightmapCollection must have a name!"
        return cls(name, **dict(enumerate(lightmaps)))

    def subset(self, pattern: str) -> List[str]:
        return LightmapCollection(self.name, **{fn: self[fn] for fn in fnmatch.filter(self.namelist(), pattern)})

    def namelist(self) -> List[str]:
        # TODO: zero-pad ints
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
        keys = [
            ".".join(map(str, k)) if isinstance(k, tuple) else k
            for k in sorted(self._lightmaps.keys())]
        return keys

    def save(self, folder: str = "./", extension: str = ".tga"):
        self.save_as(self.name, folder, extension)

    def save_as(self, name: str, folder: str = "./", extension: str = ".tga"):
        os.makedirs(folder, exist_ok=True)
        for filename in self.namelist():
            self[filename].save(os.path.join(folder, f"{name}.{filename}{extension}"))


# LightmapPage utils
AllocatedSpace = collections.namedtuple("AllocatedSpace", ["x", "y", "width", "height"])
Row = collections.namedtuple("Row", ["top", "height", "free_width"])


class LightmapPage:
    """for grouping small per-face lightmaps"""
    allocated_spaces: Dict[LightmapID, AllocatedSpace]
    # NOTE: mutating allocated_spaces does not update packing
    # -- each lightmap is packed into rows (spaces assumed to be empty)
    colour_mode: str
    collection: LightmapCollection
    name: str
    rows: List[Row]
    # properties
    child_bounds: List[Dict[str, Tuple[int, int]]]
    # ^ [{"mins": [x, y], "maxs": [x, y]}]
    image: Image.Image

    # TODO: pack w/ bleed margins
    # -- pre-bleed each image before adding it?
    # TODO: pack "styles" in series & use a `lightmap_step` UV
    # -- would have to pre-group styles for a given face into one image (with another LightmapPage?)

    def __init__(self, name: str, max_width=1024, max_height=math.inf, colour_mode="RGBA"):
        self.name = name
        self.max_width, self.max_height = max_width, max_height
        self.colour_mode = colour_mode
        self.rows = [Row(0, max_height, max_width)]
        self.allocated_spaces = dict()
        self.collection = LightmapCollection(name)

    def __repr__(self) -> str:
        dimensions = f"{self.max_width}x{self.max_height}px"
        num_lightmaps = f"{len(self)} lightmaps"
        return f"<LightmapPage {self.colour_mode} {dimensions} {num_lightmaps} @ 0x{id(self):016X}>"

    def __len__(self) -> int:
        return len(self.allocated_spaces)

    def add(self, key: Any, image: Image.Image):
        """for most effecient packing, sort images first (by height)"""
        assert key not in self.collection
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
        # remove the row allocated to if it was filled
        if row.free_width == 0:
            self.rows.pop(i)
        # record image
        self.allocated_spaces[key] = AllocatedSpace(x, y, width, height)
        self.collection[key] = image
        return self

    @classmethod
    def from_list(cls, name: str, lightmaps: List[Image], **kwargs) -> LightmapPage:
        return cls.from_collection(LightmapCollection.from_list(name, lightmaps), **kwargs)

    @classmethod
    def from_collection(cls, collection: LightmapCollection, **kwargs) -> LightmapPage:
        page = cls(collection.name, **kwargs)
        # sort by height, then width in ascending order:
        # NOTE: might be more efficient to skip the width sort
        sorted_keys = sorted(collection._lightmaps, key=lambda k: (-collection[k].size[1], -collection[k].size[0]))
        for key in sorted_keys:
            page.add(key, collection[key])
        return page

    @property
    def child_bounds(self):
        """.json-friendly"""
        return {
            ".".join(int(x) if x.isnumeric() else x for x in k): {
                "mins": [s.x, s.y],
                "maxs": [s.x + s.width, s.y + s.height]}
            for k, s in self.allocated_spaces.items()}

    @property
    def image(self):
        """Composite final image"""
        if len(self) == 0:
            return None  # empty
        width, height = self.min_width, self.min_height
        # crop to fit (can't have infinite width / height)
        # alternately, we could snap down to some power of two...
        image = Image.new(self.colour_mode, (width, height))
        for key, space in self.allocated_spaces.items():
            x, y, width, height = space
            image.paste(self.collection[key], (x, y, x + width, y + height))
        return image

    @property
    def min_width(self):
        return max([x + w for x, y, w, h in self.allocated_spaces.values()])

    @property
    def min_height(self):
        return max([y + h for x, y, w, h in self.allocated_spaces.values()])

    def save(self, folder: str = "./", extension: str = "tga"):
        self.save_as(self.name, folder, extension)

    def save_as(self, name: str, folder: str = "./", extension: str = "tga"):
        os.makedirs(folder, exist_ok=True)
        self.image.save(os.path.join(folder, f"{name}.{extension}"))
