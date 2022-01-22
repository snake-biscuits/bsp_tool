import os
import shutil
import sys

from maplist import installed_games


backup_dir = "F:/bsps"
if len(sys.argv) == 2:
    backup_dir = sys.argv[1]
print(f"Making backups in '{backup_dir}'")

i = 0
for base_dir, game_dir in installed_games:
    i += 1
    print(f"Backing up ({i}/{len(installed_games)}) {game_dir}...")
    for map_dir in installed_games[(base_dir, game_dir)]:
        src_dir = os.path.join(base_dir, game_dir, map_dir)
        dest_dir = os.path.join(backup_dir, game_dir, map_dir)
        os.makedirs(dest_dir, exist_ok=True)
        try:  # note the missed file(s) and continue
            shutil.copytree(src_dir, dest_dir, dirs_exist_ok=True)
        except shutil.Error as err:
            print(f"*** ERROR *** {err}")
        except FileNotFoundError as err:
            print(f"*** ERROR *** {err}")
