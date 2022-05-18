# `.bsp` Compile Process

## Core stages

The Official way to make a `.bsp` file is via a level editor.
Level editors save your work to a `.map` or `.vmf`

> NOTE: Some editors like `J.A.C.K.` or Half-Life's Hammer use other formats (`.jmf` & `.rmf`)

These files are made up of plaintext defining brushwork, other static geometry & entities

> NOTE: Not all entities make it into a compiled `.vmf` as entities, they are consumed by the compile process

> NOTE: Some formats also store editor session state

### BSP

| Quake      | Source     | CoD           |
| :--------- | :--------- | :------------ |
| `qbsp.exe` | `vbsp.exe` | `cod2map.exe` |

Splits level geometry up into it's various lumps & pre-calculates info for vis splitting.
Generates a "portalfile" to help the `VIS` stage.
Portalfiles can be viewed in-editor to find areas to focus optimisation on.


### VIS

| Quake     | Source     | CoD  |
| :-------- | :--------- | :--- |
| `vis.exe` | `vvis.exe` | TODO |

Generates a "pointfile" if a level "leaks".
Leaks occur when a map is not sealed off against the void, in this state, Visibility calculations fail.
Pointfiles can be viewed in-editor to track down & "seal" leaks.


### LIGHT

| Quake       | Source     | CoD  |
| :---------- | :--------- | :--- |
| `light.exe` | `vrad.exe` | TODO |

Bakes Lighting onto World Geo, also generates lighting probes & vertex lighting / lightmaps for static props.


### INFO

| Quake      | Source         | CoD  |
| :--------- | :------------- | :--- |
| `info.exe` | `vbspinfo.exe` | TODO |

Gives a breakdown of how close a given .bsp comes to engine limits


## References
[^map_format]: Quake Wiki: [Quake Map Format](https://quakewiki.org/wiki/Quake_Map_Format)
[^vmf_format]: Valve Developer Community: [Valve Map Format](https://developer.valvesoftware.com/wiki/Valve_Map_Format)

> TODO: Ericw-tools docs
