## Tools

### Level Editors

| Tool           | Link                                                                                   | Games                                |
| :------------- | :------------------------------------------------------------------------------------- | :----------------------------------- |
| CoDRadiant     | moddb.com/downloads/cod-radiant                                                        | CoD1                                 |
| CoD2Radiant    | gamefront.com/games/call-of-duty-2/file/cod2-updated-map-mod-tool                      | CoD2                                 |
| CoD4Radiant    | github.com/promod/CoD4-Mod-Tools                                                       | COD4:MW                              |
| CODWAWRadiant  | `TODO`                                                                                 |                                      |
| CSO2Converter  | git.sr.ht/~leite/cso2-bsp-converter                                                    | CS:S -> CS:O2                        |
| DarkMessiahSDK | moddb.com/games/dark-messiah-of-might-magic/downloads/dark-messiah-might-and-magic-sdk | Dark Messiah SP                      |
| GtkRadiant     | github.com/TTimo/GtkRadiant                                                            | Q3/RtCW/W:ET/SoF2/JK2/JA/EF/HL/Q2/H2 |
|                | svn.icculus.org/gtkradiant-gamepacks                                                   |                                      |
| hammer.exe     | ships with associated game(s) or Source SDK                                            | SOURCE ENGINE                        |
| MapBase        | moddb.com/mods/mapbase/downloads/mapbase-release-build                                 | Source SDK 2013                      |
| r2radiant      | github.com/F1F7Y/r2radiant                                                             | R2                                   |
| TrenchBroom    | github.com/TrenchBroom/TrenchBroom                                                     | Q/Q2/H2/Daikatana                    |
| ÜbertoolsGDK   | moddb.com/downloads/stef2-bertools-game-devolopment-kit                                | FAKK2/EF2/MOH:AA/AMA                 |
| VampireSDK     | moddb.com/mods/vtmb-unofficial-patch/downloads/bloodlines-sdk                          | VtMB                                 |

> TODO: get a list of preferred compilers from Trenchbroom's default profiles


### Compilers

| Tool            | Link                                                              | Games
| :-------------- | :---------------------------------------------------------------- | :----------------------------------- |
| Q3Map3          | github.com/siliconemilk/q3map3                                    | Q3                                   |
| ericw-tools     | github.com/ericwa/ericw-tools                                     | Q/H2/HL/RMQ                          |


### Other

| Tool            | Link                                                              | Games
| :-------------- | :---------------------------------------------------------------- | :----------------------------------- |
| BSPFix          | valvedev.info/tools/bspfix                                        | HL -> HL:BS                          |
| JBNTools        | code.google.com/archive/p/jbn-bsp-lump-tools                      | JB:N (cannot compile maps)           |
| D3DBspConverter | github.com/SE2Dev/D3DBSP_Converter                                | CoD:WaW <-> CoD:BO                   |
| Q2Tools220      | github.com/qbism/q2tools-220                                      | Q2/HL                                |
| 220Converter    | www.ogier-editor.com/mapconv                                      | Q2/Q3                                |



## Engine Branch Coverage

| BspClass        | `branch_script`                 | Editors                  | Converter     | Other      |
| :-------------- | :------------------------------ | :----------------------- | :------------ | :--------- |
| D3DBsp          | `infinity_ward.modern_warfare`  | CoD4Radiant              |               |            |
| FusionBsp       | `id_software.qfusion`           | GtkRadiant               |               |            |
| GoldSrcBsp      | `gearbox.blue_shift`            | GtkRadiant               | BSPFix        |            |
|                 | `gearbox.nightfire`             | JBNTools                 |               | JBNTools   |
|                 | `valve.goldsrc`                 | GtkRadiant               |               |            |
| IdTechBsp       | `id_software.quake2`            | GtkRadiant \ TrenchBroom |               | Q2Tools220 |
|                 | `id_software.quake3`            | GtkRadiant               |               |            |
|                 | `infinity_ward.call_of_duty1`   | CoDRadiant               |               |            |
|                 | `ion_storm.daikatana`           | TrenchBroom              |               |            |
|                 | `raven.soldier_of_fortune`      |                          |               |            |
|                 | `ritual.sin`                    |                          |               |            |
| InfinityWardBsp | `infinity_ward.call_of_duty2`   | CoD2Radiant              |               |            |
| QuakeBsp        | `id_software.quake`             | TrenchBroom              |               |            |
|                 | `raven.hexen2`                  | TrenchBroom              |               |            |
| RavenBsp        | `raven.soldire_of_fortune2`     | GtkRadiant               |               |            |
|                 | `ritual.sin`                    |                          |               |            |
| ReMakeQuakeBsp  | `id_software.remake_quake`      | GtkRadiant               |               |            |
| RespawnBsp      | `respawn.apex_legends`          |                          |               |            |
|                 | `respawn.titanfall`             |                          |               |            |
|                 | `respawn.titanfall2`            | r2radiant                |               |            |
| RitualBsp       | `ritual.fakk2`                  | ÜbertoolsGDK             |               |            |
|                 | `ritual.moh_allied_assault`     | ÜbertoolsGDK             |               |            |
|                 | `ritual.star_trek_elite_force2` | ÜbertoolsGDK             |               |            |
| ValveBsp        | `arkane.dark_messiah_sp`        | DarkMessiahSDK           |               |            |
|                 | `arkane.dark_messiah_mp`        |                          |               |            |
|                 | `loiste.infra`                  | hammer.exe               |               |            |
|                 | `nexon.cso2`                    |                          | CSO2Converter |            |
|                 | `nexon.cso2_2018`               |                          | CSO2Converter |            |
|                 | `nexon.vindictus`               |                          |               |            |
|                 | `troika.vampire`                | VampireSDK               |               |            |
|                 | `valve.alien_swarm`             | hammer.exe               |               |            |
|                 | `valve.left4dead`               | hammer.exe               |               |            |
|                 | `valve.left4dead2`              | hammer.exe               |               |            |
|                 | `valve.orange_box`              | hammer.exe               |               |            |
|                 | `valve.sdk_2013`                | hammer.exe / MapBase     |               |            |
|                 | `valve.source`                  | hammer.exe               |               |            |
