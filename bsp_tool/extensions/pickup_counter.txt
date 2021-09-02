>>> import bsp_tool
>>> tf2_bsp = bsp_tool.load_bsp("Team Fortress 2/tf/maps/pl_upward.bsp")
>>> [e["classname"] for e in tf2_bsp.ENTITIES if e["classname"].startswith("item_")]
["item_healthkit_medium", ..., "item_ammopack_medium"]
>>> {c: _.count(c) for c in set(_)}
{"item_ammopack_small": 1, "item_ammopack_medium": 15, "item_ammopack_full": 1,
"item_healthkit_small": 5, "item_healthkit_medium": 7, "item_healthkit_full": 1}
