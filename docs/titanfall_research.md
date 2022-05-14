# Titanfall rBSP format research


## Source engine basis

Titanfall (2014) was built on a fork of Valve's Source Engine around 2011 (Portal 2's engine).  
From here Respawn built on the Valve's variant of the `.bsp` format[^VDC]


## Pre-existing research

Cra0kalo & ata4 Titanfall 1 lump names
Icepick (WillCo) Titanfall 2 `.bsp` -> `.obj`
Possibly derived from a function BobTheBoc found (rediscovered?) which exports maps from the game


## Current research

Legion / Legion+ .bsp converters
.bsp viewers
reverse engineering `engine.dll`
Tools: Ida, Ghidra, Radare2, 010 Hex editor & templates
`Mod_*` functions & tracing error message strings


### `engine.dll` lump loads table

> TODO: copy .txt from desktop


### Extreme SIMD transcript & C++ `intrinsics.hpp`

> TODO: copy.txt from desktop


### using `supported/titanfall.md` & "coverage"

> TODO: explain what is listed & how coverage is calculated


### mapping lump relationships

> TODO: explain `branch_script` layout
> TODO: database normalisation / optimisation
> TODO: "parallel" lumps
> TODO: .bsp design patterns
> TODO: byte-alignment, padding & SIMD registers

