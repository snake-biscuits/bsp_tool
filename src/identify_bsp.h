/* .bsp FILE_MAGIC & BSP_VERSION values for identifying engine branches */
/* LAST REVISION: 2022-08-24 (YYYY-MM-DD) @ 00:30am */
#ifndef IDENTIFY_BSP_H
#define IDENTIFY_BSP_H

/* NOTE: not every engine branch can be precisely identified */
/* NOTE: this file should be compatible with C89 -> C++17 */


/* WARNING: don't undef base macros! you can break recursion! */
#define MAGIC(a, b, c, d)  ((a << 0)|(b << 8)|(c << 16)|(d << 24))
#define MAGIC_2015  MAGIC('2', '0', '1', '5')  /* 2015 inc. */
#define MAGIC_2PSB  MAGIC('2', 'P', 'S', 'B')  /* DEPRECATED */
#define MAGIC_BSP2  MAGIC('B', 'S', 'P', '2')  /* Various Quake Source Ports */
#define MAGIC_EALA  MAGIC('E', 'A', 'L', 'A')  /* Medal of Honor: Allied Assault - Breakthrough */
#define MAGIC_EF2_  MAGIC('E', 'F', '2', '!')  /* Ritual */
#define MAGIC_FAKK  MAGIC('F', 'A', 'K', 'K')  /* Ritual, Rogue */
#define MAGIC_FBSP  MAGIC('F', 'B', 'S', 'P')  /* QFusion */
#define MAGIC_IBSP  MAGIC('I', 'B', 'S', 'P')  /* Id, Infinity Ward */
#define MAGIC_PSBr  MAGIC('P', 'S', 'B', 'r')  /* Bluepoint (Titanfall Xbox360 port) */
#define MAGIC_PSBV  MAGIC('P', 'S', 'B', 'V')  /* Valve, Arkane (Xbox360 Big-Endian) */
#define MAGIC_RBSP  MAGIC('R', 'B', 'S', 'P')  /* Raven */
#define MAGIC_rBSP  MAGIC('r', 'B', 'S', 'P')  /* Respawn */
#define MAGIC_VBSP  MAGIC('V', 'B', 'S', 'P')  /* Arkane, Valve, Loiste, Troika, NEXON */

/* BSP_VERSION */
/* WARNING: don't undef base macros! you can break recursion! */
#define V(x, y)  (x | y << 16)  /* uint16_t[2] => uint32_t */
/* NO MAGIC */
#define VERSION_IDQ1  29   /* Quake */
#define VERSION_GSRC  30   /* Half-Life */
#define VERSION_HLBS  42   /* Half-Life: Blue Shift */
/* MAGIC_2015 */
#define VERSION_DEMO  18   /* Medal of Honor: Allied Assault (Demo) */
#define VERSION_2015  19   /* Medal of Honor: Allied Assault */
/* MAGIC_EALA */
#define VERSION_EALA  21   /* Medal of Honor: Allied Assault - Breakthrough */
/* MAGIC_EF2_ */
#define VERSION_EF2_  20   /* Star Trek: Elite Force II */
/* MAGIC_FAKK */
#define VERSION_FAKK  12   /* Heavy Metal: F.A.K.K. 2 */
#define VERSION_ALIC  42   /* American McGee's Alice */
/* MAGIC_FBSP */
#define VERSION_FBSP  1    /* Warsow */
/* MAGIC_IBSP */
#define VERSION_COD2  4    /* Call of Duty 2 */
#define VERSION_COD4  22   /* Call of Duty: Modern Warfare */
#define VERSION_IDQ2  38   /* Quake II / Anachronox / Heretic II */
#define VERSION_DAIK  41   /* Daikatana / SiN (allegedly) */
#define VERSION_IDQ3  46   /* Quake III / Quake III Team Arena */ /* NOTE: Soldier of Fortune (Q2 lumps, Q3 identifiers) */
#define VERSION_RTCW  47   /* Return to Castle Wolfenstein */
#define VERSION_COD1  59   /* Call of Duty / United Offensive */
#define VERSION_Q3DS  666  /* Quake III Mod: Dark Salvation */
/* MAGIC_RBSP */
#define VERSION_RBSP  1    /* SiN / Soldier of Fortune II / Star Wars Jedi Knight: Jedi Academy / Outcast */
/* MAGIC_rBSP */
#define VERSION_R1RE  29   /* Titanfall / Titanfall: Online */
#define VERSION_R2TT  36   /* Titanfall 2 Tech Test */
#define VERSION_R2RE  37   /* Titanfall 2 */
#define VERSION_R5S0  47   /* Apex Legends (Season 0-6) */
#define VERSION_R5S7  48   /* Season 7 */
#define VERSION_R5S8  49   /* Season 8-9 + 11.0 Depot */
#define VERSION_R5SA  50   /* Season 10 */
#define VERSION_R5SB  V(50, 1)  /* Season 11 */
#define VERSION_R5SC  V(49, 1)  /* Season 11.1 Depot */
#define VERSION_R5SD  V(51, 1)  /* Season 13 */
/* MAGIC_VBSP */
#define VERSION_CRIM  18   /* Stolen HL2 Beta */
#define VERSION_VTMB  19   /* Vampire: The Masquerade - Bloodlines / Stolen HL2 Beta */
#define VERSION_2007  20   /* Orange Box Branch / Left4Dead */
#define VERSION_2013  21   /* CS:GO / Black Mesa / Blade Symphony */
#define VERSION_XSDK  22   /* Infra */
#define VERSION_CONT  27   /* Contagion */
#define VERSION_CSO2  100  /* Counter-Strike: Online 2 */
#define VERSION_DMMM  V(20, 4)  /* Dark Messiah of Might & Magic */


/* TODO: verbose defines for each engine */
/* NOTE: avoiding aliases for reader's convenience */
/* Source Engine Family */
#define BSP_MAGIC_SOURCE_ENGINE                    MAGIC_VBSP
#define BSP_MAGIC_SOURCE_ENGINE_X360               MAGIC_PSBV
#define BSP_VERSION_HL2_BETA                       18
#define BSP_VERSION_ORANGE_BOX                     20
#define BSP_VERSION_LEFT4DEAD                      20        /* unique */
#define BSP_VERSION_VINDICTUS                      20        /* unique */
#define BSP_VERSION_DARK_MESSIAH_MP                V(20, 4)
#define BSP_VERSION_DARK_MESSIAH_SP                V(20, 4)  /* unique */
#define BSP_VERSION_SDK_2013                       21
#define BSP_VERSION_LEFT4DEAD2                     21        /* unique */
#define BSP_VERSION_INFRA                          22
#define BSP_VERSION_CONTAGION                      27
#define BSP_VERSION_CSO2_2013                      100
#define BSP_VERSION_CSO2_2018                      100       /* unique */
/* Titanfall Engine Family */
#define BSP_MAGIC_TITANFALL_ENGINE                 MAGIC_rBSP  /* NOT RBSP! */
#define BSP_MAGIC_TITANFALL_ENGINE_X360            MAGIC_PSBr
#define BSP_VERSION_TITANFALL                      29
#define BSP_VERSION_TITANFALL_ONLINE               29
#define BSP_VERSION_TITANFALL_2_TECH_TEST          36
#define BSP_VERSION_TITANFALL_2                    37
#define BSP_VERSION_APEX_LEGENDS_SEASON_0          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_1          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_2          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_3          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_4          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_5          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_6          47
#define BSP_VERSION_APEX_LEGENDS_SEASON_7          48
#define BSP_VERSION_APEX_LEGENDS_SEASON_8          49
#define BSP_VERSION_APEX_LEGENDS_SEASON_9          49
#define BSP_VERSION_APEX_LEGENDS_SEASON_10         50
#define BSP_VERSION_APEX_LEGENDS_SEASON_11         V(50, 1)
#define BSP_VERSION_APEX_LEGENDS_SEASON_11_DEPOT   V(49, 1)
#define BSP_VERSION_APEX_LEGENDS_SEASON_12         V(50, 1)
#define BSP_VERSION_APEX_LEGENDS_SEASON_13         V(51, 1)
#define BSP_VERSION_APEX_LEGENDS_SEASON_14         V(51, 1)
/* Quake III Engine Family */
#define BSP_MAGIC_QUAKE_3                          MAGIC_IBSP
#define BSP_VERSION_QUAKE_2                        38
#define BSP_VERSION_ANACHRONOX                     38
#define BSP_VERSION_HERETIC_2                      38
#define BSP_VERSION_DAIKATANA                      41
#define BSP_VERSION_SIN_IBSP                       41
#define BSP_VERSION_QUAKE_3                        46
#define BSP_VERSION_RETURN_TO_CASTLE_WOLFENSTEIN   47
#define BSP_VERSION_DARK_SALVATION                 666
/* Call of Duty Engine Family */
#define BSP_MAGIC_COD                              MAGIC_IBSP
#define BSP_VERSION_CALL_OF_DUTY                   59
#define BSP_VERSION_CALL_OF_DUTY_UNITED_OFFENSIVE  59
#define BSP_VERSION_CALL_OF_DUTY_2                 4
#define BSP_VERSION_CALL_OF_DUTY_4_MODERN_WARFARE  22


#endif  /* IDENTIFY_BSP_H */
