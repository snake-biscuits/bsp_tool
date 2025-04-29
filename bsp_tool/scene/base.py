from __future__ import annotations
import os
from typing import Dict, Generator, List, Union

from ..utils import geometry


ModelList = Union[
    List[geometry.Model],
    Dict[str, geometry.Model]]


def indent(count: int = 1) -> str:
    return " " * 4 * count  # 4 spaces, no tabs


# TODO: mount_file etc. for:
# -- .usd[acz] textures & subtrees
# -- .obj materials (.mtl)
# -- .glb binary files (.bin)
# TODO: do we use groups instead of models, like .obj?
# -- what about node trees?
# -- **better to expect a specific standard and document that standard well**
class SceneDescription:
    """base class for file formats containing multiple models etc."""
    # NOTE: formats can be lossy, reloading a saved file could result in data loss
    # -- but some formats will also contain data which we totally ignore
    models: Dict[str, geometry.Model]
    exts_txt: List[str] = list()  # text format extension
    # NOTE: txt formats are saved to file via: lines -> as_text -> save_as
    # -- tl;dr: write a .lines() so you can .save_as("filename.txt_ext")
    exts_bin: List[str] = list()  # binary format extension
    exts: List[str] = property(lambda s: [*s.exts_txt, *s.exts_bin])
    # NOTE: all extensions should be lowercase

    def __init__(self):
        self.models = dict()

    def __repr__(self) -> str:
        descriptor = "{len(self.models)} models"
        return f"<{self.__class__.__name__} {descriptor} @ 0x{id(self):016X}>"

    def lines(self) -> Generator[str, None, None]:
        """yields a text-file representation roughly one line at a time"""
        raise NotImplementedError()

    def as_text(self) -> str:
        """text format representation"""
        # NOTE: trailing newline is always nice to have
        return "\n".join(self.lines()) + "\n"

    # NOTE: we don't have any binary formats to try out just yet
    def as_bytes(self) -> bytes:
        """binary format representation"""
        raise NotImplementedError("no binary format")

    def save_as(self, filename: str):
        folder, short_filename = os.path.split(filename)
        # TODO: create folder if it doesn't exist
        if folder != "":
            assert os.path.isdir(folder), f"folder does not exist: '{folder}'"
        raw_filename, ext = os.path.splitext(short_filename)
        ext = ext.lower()
        assert ext in self.exts, f"cannot save to unknown extension: '{ext}'"
        mode, method = {
            **{
                ext: ("w", self.as_text)
                for ext in self.exts_txt},
            **{
                ext: ("wb", self.as_bytes)
                for ext in self.exts_bin}
        }[ext]
        with open(filename, mode) as out_file:
            out_file.write(method())
        # TODO: write attached files out relative to folder
        # -- this assumes they have been generated or edited by .as_text / .as_bytes
        # NOTE: we aren't using attached files yet

    @classmethod
    def from_models(cls, models: ModelList) -> SceneDescription:
        out = cls()
        if isinstance(models, (list, tuple, set)):
            models = {
                f"model_{i:03d}": model
                for i, model in enumerate(models)}
        assert isinstance(models, dict), "'models' must be a ModelList!"
        out.models = models
        return out

    # TODO: from_archive(cls, filename: str, archive: ArchiveClass)

    @classmethod
    def from_file(cls, filename: str) -> SceneDescription:
        # TODO: binary or text?
        raise NotImplementedError()

    # TODO:
    # -- from_bytes
    # -- from_file
    # -- from_stream
    # -- from_text
