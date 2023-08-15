"""!!! WARNING: THIS SCRIPT WILL CHANGE YOUR WORKING DIRECTORY! DO NOT IMPORT !!!"""
from collections import defaultdict
import os
import readline  # noqa F401  (extends input())
import subprocess
import sys
import time
from typing import Dict, List


# TODO: calculate season / patch / map dir sizes
# TODO: abridge "depot/" paths ("depot/r5launch/.../maps" -> "depot/r5launch/")
# TODO: depots_of(season, release)
# TODO: find all versions of mp_<whatever>.bsp (depots optional)
# TODO: bsp_tool.load_bsp interface
# TODO: scan all pakfiles
# TODO: index season & patch by integer
# TODO: hooks for MegaTest


#################
# PRINT COLOURS #
#################

ansi_cc = {"blk": 30, "red": 31, "grn": 32, "ylw": 33,
           "blu": 34, "mag": 35, "cyn": 36, "wht": 37}


def print_c(msg: str, col: str = "wht"):
    print(f"\x1b[{ansi_cc[col]}m{msg}\x1b[0m")


def input_c(msg: str, col: str = "wht"):
    return input(f"\x1b[{ansi_cc[col]}m{msg}\x1b[0m ")


###########
# WARNING #
###########

print_c("-===- ENTERING THE APEX ARCHIVE -===-", "grn")
if __name__ != "__main__":
    print_c("! WARNING ! The Archive does not take kindly to intruders", "ylw")
    if input_c("> Do you want to enter The Archive? [y/n]", "cyn").lower()[0] != "y":
        print_c("-===- LEAVING THE APEX ARCHIVE -===-", "grn")
        raise SystemExit


release_date_fmt = "%-d%b%y"  # e.g. 1Jan23 (note no leading 0)
# NOTE: all paths are lowercase

# TODO: ensure consistent order
dirs = {"season0": {"4feb19": (0, 0, "Preseason")},
        "season1": {"19mar19": (1, 0, "Wild Frontier"),
                    "16apr19": (1, 1, ""),
                    "4jun19": (1, 2, "Legendary Hunt")},
        "season2": {"2jul19": (2, 0, "Battle Charge"),
                    "13aug19": (2, 1, "Iron Crown"),
                    "3sep19": (2, 2, "Voidwalker")},
        "season3": {"1oct19": (3, 0, "Meltdown"),
                    "5nov19": (3, 1, ""),
                    "3dec19": (3, 2, "Holo-Day Bash")},
        "season4": {"4feb20": (4, 0, "Assimilation"),
                    "3mar20": (4, 1, "System Override")},
        # TODO:             "7apr20": (4, 2, "The Old Ways")},
        # TODO: "season5": {"12may20": (5, 0, "Fortune's Favour"),
        # TODO:             "23jun20": (5, 1, "Lost Treasures")},
        # TODO: "season6": {"18aug20": (6, 0, "Boosted"),
        # TODO:             "6oct20": (6, 1, "Aftermarket")},
        "season7": {"3nov20": (7, 0, "Ascension"),
                    "5jan21": (7, 1, "Fight Night")},
        "season8": {"2feb21": (8, 0, "Mayhem"),
                    "9mar21": (8, 1, "Chaos Theory")},
        "season9": {"4may21": (9, 0, "Legacy"),
                    "29jun21": (9, 1, "Genesis")},
        # NOTE: map format changed to (49/50, 1) around season 10
        "season10": {"3aug21": (10, 0, "Emergence"),
                     "10aug21": (10, 0, ""),
                     "14sep21": (10, 1, "Evolution"),
                     "24sep21": (10, 1, "")},
        "season11": {"2nov21": (11, 0, "Escape"),
                     "5nov21": (11, 0, ""),
                     "17nov21": (11, 0, "")},
        # TODO:             "7dec21": (11, 1, "Raiders")},
        "season12": {"8feb22": (12, 0, "Defiance"),
                     "29mar22": (12, 1, "Warriors")},
        "season13": {"10may22": (13, 0, "Saviours"),
                     "21jun22": (13, 1, "Awakening")},
        "season14": {"9aug22": (14, 0, "Hunted"),
                     "20sep22": (14, 1, "Beast of Prey"),
                     "14oct22": (14, 1, "Halloween 2022")},
        "season15": {"1nov22": (15, 0, "Eclipse"),
                     "10jan23": (15, 1, "Spellbound")},
        "season16": {"14feb23": (16, 0, "Revelry"),
                     "28mar23": (16, 1, "Sun Squad")},
        "season17": {"9may23": (17, 0, "Arsenal"),
                     "20jun23": (17, 1, "Dressed to Kill"),
                     "19jul23": (17, 1, "Thief's Bane")},
        # NOTE; maps moved to .rpak in season 18
        "season18": {"8aug23": (18, 0, "Resurrection")}}


# TODO: python-mode


#################
# VIRUTAL SHELL #
#################
# communicate working directory changes to the user

def PS1():
    # NOTE: no trailing space
    time_ = time.strftime("%H:%M")
    cwd = os.getcwd()
    if cwd.startswith("/"):  # Linux / Cygwin
        split_cwd = cwd.split("/")
        if split_cwd[2] == "e":  # ITANI_WAYSOUND
            cwd = os.path.join("E:/", *split_cwd[3:])
    rel_dir = os.path.relpath(seasons_folder, cwd)
    if cwd == seasons_folder:
        rel_dir = ""
    return f"\x1b[35m{time_} \x1b[34m{user} \x1b[33mApexArchive/{rel_dir} \x1b[35m$\x1b[0m"


def term_input(*args, **kwargs):
    return input(PS1() + " ", *args, **kwargs)


def term_print(*args, **kwargs):
    print(PS1(), *args, **kwargs)


def cd(path: str):
    # TODO: cd relative to ApexArchive/
    # -- python-mode: cd(season, patch)
    term_print("cd", path)
    os.chdir(path)


###################
# ARCHIVIST LOGIN #
###################
# user must have access to The Archive

aliases = {"Jared@ITANI_WAYSOUND": "bikkie"}

user = os.getenv("USERNAME", "")
host = os.getenv("HOSTNAME", os.getenv("COMPUTERNAME"))
user = aliases.get(f"{user}@{host}", user)

print_c(f"? GETTING CREDENTIALS FOR USER \x1b[34m{user}@{host}\x1b[35m ...", "mag")
archivists = {("bikkie", "ITANI_WAYSOUND"): "E:/Mod/ApexLegends",
              ("bikkie", "copland-bentokom-9876"): "media/bikkie/3964-39351/Mod/ApexLegends"}

if (user, host) not in archivists:
    print_c(f"! WARNING ! \x1b[34m{user}@{host}\x1b[33m is not registered as an archivist", "ylw")
    print_c("-XXX- ACTIVATING SECURITY MEASURES -XXX-", "red")
    raise SystemExit
else:
    print_c(f"-===- WELCOME ARCHIVIST: {user} -===-", "grn")
    seasons_folder = archivists[(user, host)]
    os.chdir(seasons_folder)


################
# FILE HASHING #
################

def hash_of(season: str, release: str, filepath: str) -> str:
    """retrieve hash of 'filepath' in 'season/release'"""
    # TODO: stricter matching
    # - maps/x will match depot/.../maps/x first
    # - depot/r5launch/mapname
    hashfile_name = os.path.join(season, release, "hashes.sha256")
    if not os.path.exists(hashfile_name):
        generate_hashfile(season, release)
    with open(hashfile_name) as hashfile:
        for line in hashfile:  # <hash> ./<filepath>
            if filepath in line:
                hash_, full_filepath = line.split()
                print_c(f"found: {full_filepath!r}", "ylw")
                return hash_


def first_release(filepath: str) -> (str, str):
    """first season & patch 'filepath' appears in"""
    for season, releases in dirs.items():
        for release in releases:
            full_path = os.path.join(season, release, "hashes.sha256")
            if os.path.exists(full_path):
                return " ".join([season, release])


def seasons_after(season: str) -> List[str]:
    all_seasons = list(dirs.keys())
    return all_seasons[all_seasons.index(season):]


def releases_after(season: str, release: str) -> List[str]:
    # TODO: accept dates that aren't releases
    season_releases = dirs[season]
    return season_releases[season_releases.index(release):]


# "maps/mp_rr_canyonlands_64k_x_64k.bsp" -> {"sha256 hash": ["season/release", ...]}
def hash_history(filepath: str) -> Dict[str, List[str]]:
    """list hashes of 'filepath' across all seasons"""
    out = defaultdict(list)
    season, release = first_release(filepath).split()
    seasons = {season: releases_after(season, release)}
    seasons.update({s: dirs[s] for s in seasons_after(season)})
    for season, releases in seasons.items():
        for release in releases:
            hash_ = hash_of(season, release, filepath)
            if hash_ is not None:
                out[hash_].append(f"{season}/{release}")
    return out


def generate_hashfile_linux():
    """make 'hashes.sha256' in the local dir"""
    fn_patterns = ("*.bsp", "*.ent", "*.bsp_lump", "*.bsp_lump.client")
    # NOTE: "*.client" is for season 18 onwards, could apply to lots of files
    fn_filter = " -o ".join([f"-name '{f}'" for f in fn_patterns])
    bash_command = " ".join([r"find -type f \(", fn_filter, r"\) -exec sha256sum -b {} \;"])
    # NOTE: "find" & "sha256sum" are common linux utilities
    print("$", bash_command)
    with open("hashes.sha256", "w") as hashfile:
        subprocess.run(bash_command, shell=True, stdout=hashfile)


def generate_hashfile(season: str, release: str):
    """VERY DANGEROUS; changes working directoy & runs a bash command; BE CAREFUL"""
    cd(os.path.join(seasons_folder, season, release))
    if sys.platform in ("cygwin", "linux"):
        generate_hashfile_linux()
    # TODO: elif sys.platform in ("win32",): generate_hashfile_windows()
    else:
        cd(seasons_folder)
        raise NotImplementedError(f"Cannot generate hashfile: platform='{sys.platform}'")
    cd(seasons_folder)


def regen_archive_hashfiles():
    """regenerate hashfiles for the entire archive"""
    if input("? regenerate all hashfiles? [y/n] ").lower()[0] != "y":
        return
    for season, releases in dirs.items():
        for release in releases:
            cd(os.path.join(seasons_folder, season, release))
            if sys.platform in ("cygwin", "linux"):
                generate_hashfile_linux()
            else:
                raise NotImplementedError(f"Cannot generate hashfile: platform='{sys.platform}'")
    cd(seasons_folder)


if __name__ == "__main__":
    def term_help(tool=None):
        if tool is None:
            for tool_args, (desc, func) in tools.items():
                print(f"{tool_args:<16} {desc}")
        else:
            for tool_args, (desc, func) in tools.items():
                if tool_args.split()[0] == tool:
                    print(f"{tool_args:<16} {desc}")

    def term_wrap(func):
        """<func(*args: str) -> None | str | List[str]> -> terminal function"""
        def wrapped(func):
            def call(*args):
                func_out = func(*args)
                if func_out is None:  # -> None: no lines
                    return
                elif isinstance(func_out, list):  # -> List[str] => many lines
                    {print(o) for o in func_out}
                else:  # -> str => 1 line
                    print(func_out)
            return call
        return (func.__doc__, wrapped(func))

    # NOTE: tools may only have 1 instance for each arg count!
    tools = {"help": ("list all tools", term_help),
             "help tool": ("explain tool", term_help),
             # TODO: "cd season patch": term_wrap(cd),
             "seasons": ("list all seasons", lambda: {print(s) for s in dirs}),
             "patches season": ("list all patches in season", lambda s: {print(p) for p in dirs[s]}),
             "history filepath": term_wrap(hash_history),
             "hash season patch filepath": term_wrap(hash_of),
             "first filepath": term_wrap(first_release),
             "regen": term_wrap(regen_archive_hashfiles)}
    # ^ {"tool *args": ("description", function)}

    def tool_signature(tool_args: str):
        tool, *args = tool_args.split()
        return (tool, len(args))

    use = {tool_signature(t): f for t, (d, f) in tools.items()}
    known_tools = {t for (t, la) in use}
    logouts = ("logout", "quit", "q")
    tools.update({c: ("close terminal", None) for c in logouts})

    exit_terminal = False
    print_c("-===- ARCHIVE TERMINAL ONLINE -===-", "cyn")
    # TODO: quotes separated command args
    while exit_terminal is False:
        command = term_input()
        if command in logouts:
            exit_terminal = True
        elif command != "":
            tool, *args = command.split()
            tool_variant = tool_signature(command)
            if tool not in known_tools:
                print(f"! '{tool}' not found")
            elif tool_variant not in use:
                print(f"! invalid arguments for '{tool}'")
                term_help(tool)
            else:
                try:
                    use[tool_variant](*args)
                except Exception as exc:
                    print(f"! ERROR ! {exc!r}")
    print_c("-===- LOGGED OUT OF ARCHIVE TERMINAL -===-", "cyn")
