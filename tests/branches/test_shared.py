from typing import Dict, List

from bsp_tool.branches.shared import Entities

import pytest


# TODO: make sure errors / warnings are raised for bad parses

cases = {"one_entity": [dict(classname="worldspawn")],
         "two_entities": [dict(classname="worldspawn"), dict(classname="info_player_start")],
         "one_newline_in_value": [dict(classname="worldspawn", message="map\nby author")],
         "two_newlines_in_value": [dict(classname="ent_text", message="now playing\nsong\nby artist")],
         "curly_brace_in_value": [dict(classname="worldspawn", message="lorem {ipsum} dolor demet")]}


def entity(**key_value_pairs) -> bytes:
    """opposite of the parser, makes comparing results easier"""
    out = ["{", *[f'"{k}" "{v}"' for k, v in key_value_pairs.items()], "}"]
    return b"\n".join([bytes(x, "ascii") for x in out])


class TestEntities:
    @pytest.mark.parametrize("expected", cases.values(), ids=cases.keys())
    def test_generic(self, expected: List[Dict[str, str]]):
        raw = b"\n".join([entity(**d) for d in expected])
        parsed = Entities.from_bytes(raw)
        assert len(parsed) == len(expected)
        for expected_dict, parsed_dict in zip(expected, parsed):
            assert parsed_dict == expected_dict

    def test_ignore_comment(self):
        """sven co-op yabma.bsp"""
        expected = [dict(classname="worldspawn"), dict(classname="info_player_start")]
        raw = b"\n".join([entity(**expected[0]), b"// C++ style comment", *[entity(**d) for d in expected[1:]]])
        parsed = Entities.from_bytes(raw)
        assert len(parsed) == len(expected)
        for expected_dict, parsed_dict in zip(expected, parsed):
            assert parsed_dict == expected_dict

    def test_curly_whitespace(self):
        """some sven co-op maps"""
        expected = [dict(classname="worldspawn")]
        raw = entity(**expected[0])

        def parse_and_check(raw):
            parsed = Entities.from_bytes(raw)
            assert len(parsed) == len(expected)
            for expected_dict, parsed_dict in zip(expected, parsed):
                assert parsed_dict == expected_dict

        parse_and_check(raw.replace(b"{", b" \t{\t "))
        parse_and_check(raw.replace(b"}", b" \t}\t "))

    def test_null_terminated(self):
        """some sven co-op maps"""
        expected = [dict(classname="worldspawn")]
        raw = b"".join([entity(**expected[0]), b"\0"])
        parsed = Entities.from_bytes(raw)
        assert len(parsed) == len(expected)
        for expected_dict, parsed_dict in zip(expected, parsed):
            assert parsed_dict == expected_dict

    def test_null_terminated_after_newline(self):
        """some sven co-op maps"""
        expected = [dict(classname="worldspawn")]
        raw = b"\n".join([entity(**expected[0]), b"\0"])
        parsed = Entities.from_bytes(raw)
        assert len(parsed) == len(expected)
        for expected_dict, parsed_dict in zip(expected, parsed):
            assert parsed_dict == expected_dict

    def test_null_terminated_and_trailing_whitespace(self):
        """Counter-Strike: Condition Zero Deleted Scenes cz_alamo2.bsp"""
        expected = [dict(classname="worldspawn")]
        raw = b"".join([entity(**expected[0]), b"\0 \t"])
        parsed = Entities.from_bytes(raw)
        assert len(parsed) == len(expected)
        for expected_dict, parsed_dict in zip(expected, parsed):
            assert parsed_dict == expected_dict
