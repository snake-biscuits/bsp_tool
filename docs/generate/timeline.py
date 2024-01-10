from __future__ import annotations
import math
import re
from typing import List, Union

# TODO: import sql database
# TODO: platform svgs (like vndb.org, but don't just copy theirs)
# TODO: game icon svgs (major titles first: Quake Series, Half-Life Series, Titanfall Series)

# TODO: merge multiple title releases in the same month
# -- Release.can_merge_with(other: Release)
# --- same game (also Dark Messiah MP + SP)
# -- Release + Release
# --- combine regions
# --- combine fuzzy date range
# --- combine branches

# TODO: other markers
# -- Apex Legends seasons
# -- Updates (branch changes) [CSO:2, Vindictus, Apex Legends]

# TODO: CSS
# TODO: generate css classes for branches & mixed branches
# -- sql/branch.data.colour.json
# TODO: beta - dotted border-style
# TODO: demo - dashed border-style
# TODO: season - Date marker w/ hover effect

# TODO: COLUMNS
# TODO: grouping & sorting
# -- one per branch? share & reuse

# TODO: TRAILS
# -- same game, new platform / region / branch
# TODO: sql db: GameRelation
# TODO: fade to transparent when sharing w/ other branches?
# -- horizontal connectors
# -- rounded corner s-curves?

# TODO: HTML NODE TREE
# -- timeline
# --  year
# --    year-label: 1996-2023
# --    columns: 1-4 (grouping relationships [engine, series etc.])
# --      months: jan-dec
# --        release: game / beta / demo / season
# --          icon: .svg
# --          name
# --          platform: .svg
# --          region: emoji


# CSS classes for calendar positions
months = [
    "jan", "feb", "mar", "apr",
    "may", "jun", "jul", "aug",
    "sep", "oct", "nov", "dec"]

# Emoji Regional Indicators
regions = {
    # "AUS": "\U0001F1E6\U0001F1FA",  # flag: Australia
    "EU": "\U0001F1EA\U0001F1FA",  # flag: European Union Flag
    "JP": "\U0001F1EF\U0001F1F5",  # flag: Japan
    "KOR": "\U0001F1F0\U0001F1F7",  # flag: South Korea
    "NA": "\U0001F1FA\U0001F1F8",  # flag: United States
    "RU": "\U0001F1F7\U0001F1FA",  # flag: Russia
    "WW": "\U0001F310"}  # globe with meridians

# Short names for "branch-mix-..." CSS classes
short_branches = {
    # id_software
    "quake": "q",
    "quake2": "q2",
    "quake3": "q3",
    "remakequake": "rmq",
    "quake64": "q64"
}

csv_columns = [
    "Developer", "Game", "Released", "Region", "Platform", "Delisted", "Branch Script"]


class FuzzyInt:
    """Approximate base 10 integer"""
    digits: List[Union[int, ...]]
    # 199? > 198?
    # 199? != 1990..1999
    # 199? < 2000
    # TODO: within(self, other) -> bool:  # lives inside other's range

    def __init__(self, string: str):
        assert re.match(r"[0-9\?]+", string)
        self.digits = [c if c != "?" else Ellipsis for c in string]

    def __repr__(self) -> str:
        return f'FuzzyInt("{self!s}")'

    def __str__(self) -> str:
        return "".join([str(d) if d is not Ellipsis else "?" for d in self.digits])

    def __eq__(self, other: Union[FuzzyInt, float]):
        if isinstance(other, FuzzyInt):
            return self.digits == other.digits
        elif isinstance(other, (int, float)):
            return False
        else:
            raise TypeError(f"cannot compare FuzzyInt w/ {type(other)}")

    def __gt__(self, other: Union[FuzzyInt, float]):
        if isinstance(other, FuzzyInt):
            if len(self.digits) == len(other.digits):
                return self.lower_limit > other.upper_limit
            else:
                return len(self.digits) > len(other.digits)
        elif isinstance(other, (int, float)):
            return self.lower_limit > other  # definitely bigger
        else:
            raise TypeError(f"cannot compare FuzzyInt w/ {type(other)}")

    def __lt__(self, other: Union[FuzzyInt, float]):
        if isinstance(other, FuzzyInt):
            if len(self.digits) == len(other.digits):
                return self.upper_limit < other.lower_limit
            else:
                return len(self.digits) < len(other.digits)
        elif isinstance(other, (int, float)):
            return self.upper_limit < other  # definitely smaller
        else:
            raise TypeError(f"cannot compare FuzzyInt w/ {type(other)}")

    @property
    def lower_limit(self) -> int:
        return int(str(self).replace("?", "0"))

    @property
    def upper_limit(self) -> int:
        return int(str(self).replace("?", "9"))

    def is_fuzzy(self) -> bool:
        return Ellipsis in self.digits

    def as_int(self) -> int:
        if self.is_fuzzy():
            raise RuntimeError(f"Cannot convert {self} to int")
        return int(self.digits)


class FuzzyDate:
    # expected range: 1996-01-01 -> 2024-12-31
    year: FuzzyInt
    month: FuzzyInt
    day: FuzzyInt

    def __init__(self, year=..., month=..., day=...):
        self.year = year
        self.month = month
        self.day = day

    def __repr__(self) -> str:
        return f'FuzzyDate.from_string("{self.year!s}-{self.month!s}-{self.day!s}")'

    def __eq__(self, other: FuzzyDate) -> bool:
        if not isinstance(other, FuzzyDate):
            return False
        return (self.year, self.month, self.day) == (other.year, other.month, other.day)

    def __lt__(self, other: FuzzyDate) -> bool:
        if not isinstance(other, FuzzyDate):
            return False
        return (self.year, self.month, self.day) < (other.year, other.month, other.day)

    @classmethod
    def from_string(cls, string: str):
        # NOTE: most delisted dates are "", representing a quantum state of potential future delisting
        if string == "Never" or string == "":  # Unreleased / Unknown
            return cls(..., ..., ...)
        elif string == "Not Yet":  # Future release
            return cls(year=math.inf)
        elif re.match(r"[0-9\?]{4}-[0-9\?]{2}-[0-9\?]{2}", string):
            return cls(*map(FuzzyInt, string.split("-")))
        else:
            raise RuntimeError(f"couldn't initialise from: {string!r}")


class Release:
    developers: List[str]
    game: str
    date: FuzzyDate
    regions: List[str]
    platforms: List[str]
    branches: List[str]

    def __init__(self, dev="", game="", released="", region="", platform="", delisted="", branch=""):
        self.developers = dev.split(";")
        self.game = game
        # TODO: game type (Beta, Demo, Season)
        self.date = FuzzyDate.from_string(released)
        self.regions = dev.split(";")
        self.platforms = dev.split(";")
        self.delisted = FuzzyDate.from_string(delisted)
        self.branches = branch.split(";")

    @property
    def region_emoji(self) -> str:
        return "".join([regions[r] for r in self.regions])

    @property
    def css_month(self) -> str:
        return months[self.date.month.as_int() - 1]

    @property
    def css_branch_class(self) -> str:
        if len(self.branches) == 1:
            return f"branch-{self.branches[0].split('.')[-1]}"
        else:
            branches = [b.split(".")[-1] for b in self.branches]
            branches = "-".join([short_branches[b] for b in branches])
            return f"branch-mix-{branches}"

    # TODO: platform icons property

    def as_html(self) -> str:
        # TODO: type class (game, beta, demo)
        # TODO: icon svg
        # TODO: platform svgs
        platforms = " ".join(self.platforms)
        nodes = [
            f'<div class="game {self.css_branch_class}">',
            f'<div class="name">{self.game}</div>',
            f'<div class="platform">{platforms}</div>',
            f'<div class="region">{self.region_emoji}</div>',
            "</div>"]
        return "".join(nodes)  # one line
