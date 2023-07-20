import difflib
from typing import Dict, Generator, List

from . import base


class EntitiesDiff(base.Diff):
    def short_stats(self) -> str:
        # NOTE: ignoring lump order changes, but key-value order is still checked
        old = {tuple(e.items()) for e in self.old}
        new = {tuple(e.items()) for e in self.new}
        added = len(new.difference(old))
        removed = len(old.difference(new))
        return f"{added} insertions(+) {removed} deletions(-)"

    def unified_diff(self) -> Generator[str, None, None]:  # SLOW!
        # TODO: meta-diff to align indices given insertions & deletions
        # -- then come back in & abridge where helpful
        # 3 reprs (inline: meta-diff, abridged: short diff line, multi-line: detailed diff)
        for old_entity, new_entity in zip(self.old, self.new):
            if not old_entity["classname"] == new_entity["classname"]:  # abridged
                yield f"- {self.short_repr(old_entity)}\n"
                yield f"+ {self.short_repr(new_entity)}\n"
            elif old_entity != new_entity:  # likely to be a little similar
                old = [f"{x}\n" for x in self.long_repr(old_entity)]
                new = [f"{x}\n" for x in self.long_repr(new_entity)]
                for line in difflib.Differ().compare(old, new):
                    yield line
            else:  # skip matching entities
                continue
        # quick leftovers
        if len(self.old) > len(self.new):
            for deleted in self.old[len(self.new):]:
                yield f"- {self.short_repr(deleted)}\n"
        elif len(self.new) > len(self.old):
            for added in self.new[len(self.old):]:
                yield f"+ {self.short_repr(added)}\n"

    @staticmethod
    def short_repr(entity: Dict[str, str]) -> str:
        classname = entity["classname"]
        origin = entity.get("origin", "")
        model = entity.get("model", "")
        if model.startswith("*"):  # brush entity
            if origin != "":
                return f"<{classname} (model {model}) @ {origin}>"
            else:  # worldspawn?
                return f"<{classname} (model {model})>"
        else:  # point entity
            if origin != "":
                return f"<{classname} @ {origin}>"
            else:
                return f"<{classname}>"

    @staticmethod
    def long_repr(entity: Dict[str, str]) -> List[str]:
        out = list()
        for key, value in entity.items():
            if isinstance(value, list):  # duplicate key (Source Input/Output)
                out.extend([f'"{key}" "{v}"' for v in value])
            else:
                out.append(f'"{key}" "{value}"')
        return ["{", *out, "}"]
