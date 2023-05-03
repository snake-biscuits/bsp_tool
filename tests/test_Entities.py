from typing import Dict, List

from bsp_tool.branches.shared import Entities

import pytest


# TODO: make sure errors / warnings are raised for bad parses


cases = {"one_entity": [dict(classname="worldspawn")],
         "two_entities": [dict(classname="worldspawn"), dict(classname="info_player_start")],
         "value_contains_one_newline": [dict(classname="worldspawn", message="map\nby author")],
         "value_contains_two_newlines": [dict(classname="ent_text", message="now playing\nsong\nby artist")],
         "contains_curly_brace": [dict(classname="worldspawn", message="lorem {ipsum} dolor demet")]}


def entity(**key_value_pairs) -> bytes:
    """opposite of the parser, makes comparing results easier"""
    out = ["{", *[f'"{k}" "{v}"' for k, v in key_value_pairs.items()], "}"]
    return b"\n".join([bytes(x, "ascii") for x in out])


@pytest.mark.parametrize("expected", cases.values(), ids=cases.keys())
def test_generic(expected: List[Dict[str, str]]):
    """Reduce, Reuse, Recycle applies to code too"""
    raw = b"\n".join([entity(**d) for d in expected])
    parsed = Entities.from_bytes(raw)
    assert len(parsed) == len(expected)
    for expected_dict, parsed_dict in zip(expected, parsed):
        assert parsed_dict == expected_dict


def test_ignore_comment():
    expected = [dict(classname="worldspawn"), dict(classname="info_player_start")]
    raw = b"\n".join([entity(**expected[0]), b"// C++ style comment", *[entity(**d) for d in expected[1:]]])
    parsed = Entities.from_bytes(raw)
    assert len(parsed) == len(expected)
    for expected_dict, parsed_dict in zip(expected, parsed):
        assert parsed_dict == expected_dict
