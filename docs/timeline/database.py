timeline_csv = """1992, Wolfenstein 3D
1993, Doom
1994, Doom II
1996, Quake
1997, Quake II
1998, Half-Life
1999, Quake III
2003, Call of Duty, Half-Life 2
2004, Doom 3
2007, The Orange Box
2011, Portal 2, Rage
2014, Titanfall
2016, Doom (2016), Titanfall 2, Dishonored 2
2019, Apex Legends"""

# 18 game skeleton
timeline = dict()
for line in timeline_csv.split("\n"):
    year, *games = line.split(", ")
    timeline[year] = [*games]
