"""Nexon is a South Korean / Japanese developer
They have worked with both Valve & Respawn's Source Engine (CS:O & TF:O [cancelled])"""
from . import cso2  # CounterStrike Online 2
from . import cso2_2018
from . import vindictus


scripts = [cso2, cso2_2018, vindictus]

titanfall_online = """Titanfall: Online was a planned F2P Titanfall spin-off developed by Respawn Entertainment & Nexon.
An open beta was held in August & September of 2017[1][2], the game was later cancelled in 2018[3].
Sources:
[1] https://titanfall.fandom.com/wiki/Titanfall_Online
[2] https://twitter.com/ZhugeEX/status/893143346021105665
[3] https://kotaku.com/titanfall-online-cancelled-in-south-korea-1827440902

Titanfall: Online's .bsp format is near identical to titanfall's
the only known difference is no .bsp_lump files are used & files are stored in Nexon's proprietary .pkg archives
Files from the Titanfall:Online closed beta can be found in the internet archive @:
https://archive.org/details/titanfall-online_202107"""
