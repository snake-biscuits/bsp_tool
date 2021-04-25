import collections
import fnmatch
import os
from typing import Dict

from .. import load_bsp
from ..branches.shared import Entities


def read_all_bsp_ents(maps_dir: str):
    for map_name in fnmatch.filter(os.listdir(maps_dir), "*.bsp"):
        bsp = load_bsp(os.path.join(maps_dir, map_name))
        map_name = os.path.splitext(map_name)[0]
        os.makedirs(f"fgd_gen_files/{map_name}", exist_ok=True)
        map_ents = collections.defaultdict(list)
        for entity in bsp.ENTITIES:
            map_ents[entity["classname"]].append(entity)
        for classname in map_ents:
            with open(f"fgd_gen_files/{map_name}/{classname}", "w") as entity_file:
                for entity in map_ents[classname]:
                    entity_file.write("\n".join(["{",
                                                 *[f'\t"{k}" "{v}"' for k, v in entity.items()],
                                                 "}\n"]))


def read_all_rbsp_ents(maps_dir: str):
    for map_name in fnmatch.filter(os.listdir(maps_dir), "*.bsp"):
        bsp = load_bsp(os.path.join(maps_dir, map_name))
        map_name = os.path.splitext(map_name)[0]
        os.makedirs(f"fgd_gen_files/{map_name}", exist_ok=True)
        map_ents = collections.defaultdict(list)
        all_entities = (*bsp.ENTITIES, *bsp.ENTITIES_env, *bsp.ENTITIES_fx,
                        *bsp.ENTITIES_script, *bsp.ENTITIES_snd, *bsp.ENTITIES_spawn)
        for entity in all_entities:
            map_ents[entity["classname"]].append(entity)
        for classname in map_ents:
            with open(f"fgd_gen_files/{map_name}/{classname}", "w") as entity_file:
                for entity in map_ents[classname]:
                    entity_file.write("\n".join(["{",
                                                 *[f'\t"{k}" "{v}"' for k, v in entity.items()],
                                                 "}\n"]))


# TODO: check each field of every classname
# -- collect every field in a set()
# -- note ranges and infer field mesh_types
# -- infer defaults

def infer_types(ent_dump_folder: str) -> Dict[str, Dict[str, set]]:  # point at fgd_gen_files
    # ^ {"classname": {"field": {"value", "other_value"}}}
    # classname is always :str
    # targetname is always :str
    # parent is always :str
    all_entries = dict()
    for map_folder in os.listdir(ent_dump_folder):
        map_folder = os.path.join(ent_dump_folder, map_folder)
        if not os.path.isdir(map_folder):
            continue
        for classname in os.listdir(map_folder):
            if classname not in all_entries:
                all_entries[classname] = collections.defaultdict(set)
            entity_filename = os.path.join(map_folder, classname)
            with open(entity_filename, "rb") as entity_file:
                map_entities = Entities(entity_file.read())
                for entity in map_entities:
                    for field, value in entity.items():
                        all_entries[classname][field].add(value)
    return all_entries


def save_ent_stats(all_entries: Dict[str, Dict[str, set]]):
    txt_file = open("findings.txt", "w")
    for entity in sorted(all_entries):
        txt_file.write(f"*** {entity} ***" + "\n")
        for field in sorted(all_entries[entity]):
            txt_file.write(field + "\n")
            txt_file.write("\n".join("\t" + v for v in sorted(all_entries[entity][field])))
            txt_file.write("\n\n")
    txt_file.close()
