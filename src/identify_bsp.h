/* .bsp FILE_MAGIC & BSP_VERSION values for identifying engine branches */
/* LAST REVISION: 2022-07-24 (YYYY-MM-DD) @ 15:30pm */

/* NOTE: not every engine branch can be precisely identified */
/* NOTE: this file should be compatible with C89 -> C++17 */


/* NOTE: MAGIC can be used elsewhere, so don't undef it! */
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
/* NOTE: MAGIC can be used elsewhere, so don't undef it! */

/* BSP_VERSION */
#define V(x, y)  (x | y << 16)  /* uint16_t[2] => uint32_t */
/* NO MAGIC */
#define VERSION_IDQ1  29  /* Quake */
#define VERSION_GSRC  30  /* Half-Life */
/* MAGIC_2015 */
#define VERSION_DEMO  18  /* Medal of Honor: Allied Assault (Demo) */
#define VERSION_2015  19  /* Medal of Honor: Allied Assault */
/* MAGIC_EALA */
#define VERSION_EALA  21  /* Medal of Honor: Allied Assault - Breakthrough */
/* MAGIC_EF2_ */
#define VERSION_EF2_  20  /* Star Trek: Elite Force II */
/* MAGIC_FAKK */
#define VERSION_FAKK  12  /* Heavy Metal: F.A.K.K. 2 */
#define VERSION_ALIC  42  /* American McGee's Alice */
/* MAGIC_FBSP */
#define VERSION_FBSP   1  /* Warsow */
/* MAGIC_IBSP */
#define VERSION_COD2   4  /* Call of Duty 2 */
#define VERSION_COD4  22  /* Call of Duty: Modern Warfare */
#define VERSION_IDQ2  38  /* Quake II / Anachronox / Heretic II */
#define VERSION_DAIK  41  /* Daikatana / SiN (allegedly) */
#define VERSION_IDQ3  46  /* Quake III / Quake III Team Arena */ /* NOTE: Soldier of Fortune (Q2 lumps, Q3 identifiers) */
#define VERSION_RTCW  47  /* Return to Castle Wolfenstein */
#define VERSION_COD1  59  /* Call of Duty / United Offensive */
#define VERSION_Q3DS  666 /* Quake III Mod: Dark Salvation */
/* MAGIC_RBSP */
#define VERSION_RBSP   1  /* SiN / Soldier of Fortune II / Star Wars Jedi Knight: Jedi Academy / Outcast */
/* MAGIC_rBSP */
#define VERSION_RER1  29  /* Titanfall / Titanfall: Online */
#define VERSION_R2TT  36  /* Titanfall 2 Tech Test */
#define VERSION_RER2  37  /* Titanfall 2 */
#define VERSION_R5S0  47  /* Apex Legends (Season 0-6) */
#define VERSION_R5S7  48  /* Season 7 */
#define VERSION_R5S8  49  /* Season 8-9 + 11.0 Depot */
#define VERSION_R5SA  50  /* Season 10 */
#define VERSION_R5SB  V(50, 1)  /* Season 11 */
#define VERSION_R5SC  V(49, 1)  /* Season 11.1 Depot */
#define VERSION_R5SD  V(51, 1)  /* Season 13 */
/* MAGIC_VBSP */
#define VERSION_CRIM  18  /* Stolen HL2 Beta */
#define VERSION_VTMB  19  /* Vampire: The Masquerade - Bloodlines / Stolen HL2 Beta */
#define VERSION_2007  20  /* Orange Box Branch / Left4Dead */
#define VERSION_2013  21  /* CS:GO / Black Mesa / Blade Symphony */
#define VERSION_XSDK  22  /* Infra */
#define VERSION_CONT  27  /* Contagion */
#define VERSION_CSO2  100 /* Counter-Strike: Online 2 */
#define VERSION_DMMM  V(20, 4)  /* Dark Messiah of Might & Magic */


/* TODO: verbose defines for each engine */
/* Source Engine Family */
#define BSP_MAGIC_SOURCE_ENGINE        MAGIC_VBSP
#define BSP_VERSION_SOURCE_HL2_BETA    18
#define BSP_VERSION_SOURCE_ORANGE_BOX  20
#define BSP_VERSION_SOURCE_LEFT4DEAD   20        /* unique */
#define BSP_VERSION_SOURCE_VINDICTUS   20        /* unique */
#define BSP_VERSION_SOURCE_DARK_M_MP   V(20, 4)
#define BSP_VERSION_SOURCE_DARK_M_SP   V(20, 4)  /* unique */
#define BSP_VERSION_SOURCE_SDK_2013    21
#define BSP_VERSION_SOURCE_LEFT4DEAD2  21        /* unique */
#define BSP_VERSION_SOURCE_INFRA       22
#define BSP_VERSION_SOURCE_CONTAGION   27
#define BSP_VERSION_SOURCE_CSO2_2013   100
#define BSP_VERSION_SOURCE_CSO2_2018   100       /* unique */

