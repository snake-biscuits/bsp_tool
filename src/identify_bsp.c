/* C89 (ANSI C) COMPATIBLE! */
#include <stdint.h>
#include <stdio.h>


/* TODO: Move MAGIC macros & VERSION macros to identify.h */
#define MAGIC(a, b, c, d)  ((a << 0)|(b << 8)|(c << 16)|(d << 24))
#define MAGIC_2015  MAGIC('2', '0', '1', '5')  /* 2015 inc. */
#define MAGIC_2PSB  MAGIC('2', 'P', 'S', 'B')  /* DEPRECATED */
#define MAGIC_BSP2  MAGIC('B', 'S', 'P', '2')  /* Various Quake Source Ports */
#define MAGIC_EF2_  MAGIC('E', 'F', '2', '!')  /* Ritual */
#define MAGIC_FAKK  MAGIC('F', 'A', 'K', 'K')  /* Ritual, Rogue */
#define MAGIC_FBSP  MAGIC('F', 'B', 'S', 'P')  /* QFusion */
#define MAGIC_IBSP  MAGIC('I', 'B', 'S', 'P')  /* Id, Infinity Ward */
#define MAGIC_PSBr  MAGIC('P', 'S', 'B', 'r')  /* Bluepoint (Titanfall Xbox360 port) */
#define MAGIC_PSBV  MAGIC('P', 'S', 'B', 'V')  /* Valve, Arkane (Xbox360 Big-Endian) */
#define MAGIC_RBSP  MAGIC('R', 'B', 'S', 'P')  /* Raven */
#define MAGIC_rBSP  MAGIC('r', 'B', 'S', 'P')  /* Respawn */
#define MAGIC_VBSP  MAGIC('V', 'B', 'S', 'P')  /* Arkane, Valve, Loiste, Troika, NEXON */

#define V(x, y)  (x | y << 16)  /* uint16_t[2] => uint32_t */

/* NO MAGIC */
#define VERSION_IDQ1  29
#define VERSION_GSRC  30
/* MAGIC_2015 */
#define VERSION_2015  19  /* Medal of Honor: Allied Assault */
/* MAGIC_EF2_ */
#define VERSION_EF2_  20  /* Star Trek: Elite Force II */
/* MAGIC_FAKK */
#define VERSION_FAKK  12  /* Heavy Metal: F.A.K.K. 2 */
#define VERSION_ALIC  42  /* American McGee's Alice */
/* MAGIC_FBSP */
#define VERSION_FBSP   1  /* Warsow */
/* MAGIC_IBSP */
#define VERSION_IDQ2  38  /* Quake II / Anachronox / Heretic II */
#define VERSION_IDQ3  46  /* Quake III / Quake III Team Arena */
#define VERSION_RTCW  47  /* Return to Castle Wolfenstein */
#define VERSION_Q3DS  666 /* Quake III Mod: Dark Salvation */
#define VERSION_COD1  59  /* Call of Duty / United Offensive */
#define VERSION_COD2   4  /* Call of Duty 2 */
#define VERSION_COD4  22  /* Call of Duty: Modern Warfare */
#define VERSION_DAIK  41  /* Daikatana */
#define VERSION_SOLD  46  /* Soldier of Fortune */
/* MAGIC_RBSP */
#define VERSION_RBSP   1  /* SiN / Soldier of Fortune II / Star Wars Jedi Knight: Jedi Academy / Outcast */
/* MAGIC_VBSP */
#define VERSION_CRIM  18  /* Stolen HL2 Beta */
#define VERSION_VTMB  19  /* Vampire: The Masquerade - Bloodlines / Stolen HL2 Beta */
#define VERSION_2007  20  /* Orange Box Branch / Left4Dead */
#define VERSION_2013  21  /* CS:GO / Black Mesa / Blade Symphony */
#define VERSION_XSDK  22  /* Infra */
#define VERSION_CSO2  100 /* Counter-Strike: Online 2 */
#define VERSION_DMMM  V(20, 4)  /* Dark Messiah of Might & Magic */
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

/* Utilities */
#define BIG_ENDIAN  v = MAGIC(v >> 24, v >> 16 & 0xFF, v >> 8 & 0xFF, v & 0xFF);
#define CASE_X(x, y)  case x##_##y: goto JMP_##y;
#define CASE_MAGIC(x)  CASE_X(MAGIC, x)
#define CASE_VERSION(x)  CASE_X(VERSION, x)
#define CONFIRM(x)  if (v!=x) fprintf(stderr, "WARNING: unexpected .bsp version (v%d; expected v%d)", v, x);
#define READ_X(x)  fread(x, sizeof(uint32_t), 1, f);
#define READ  READ_X(&m) READ_X(&v)
#define REPORT_X(x)  printf(x "\n"); break;
#define REPORT_ID(x)  REPORT_X("Id Software: " x)
#define REPORT_IW(x)  REPORT_X("Infinity Ward: " x)
#define REPORT_SOURCE(x)  REPORT_X("Source Engine: " x "branch")
#define REPORT_TITAN(x)  REPORT_X("Titanfall Engine: " x)
#define REPORT_APEX(x)  REPORT_X("Apex Legends (Season " x ")")

#define BASIC(x, y)  JMP_##x: printf(y "\n"); goto JMP_NEXT;
#define UNIQUE(x, y)  JMP_##x: printf(y "\n"); CONFIRM(VERSION_##x); goto: JMP_NEXT;


int main(int c, char** a) {
    FILE     *f;
    uint32_t  m, v;

    goto JMP_STRT;
/* TODO: report conflicting identifiers clearly */
UNIQUE(2015, "Medal of Honor: Allied Assault (by 2015 Inc.)")
UNIQUE(EF2_, "Star Trek: Elite Force II (by Ritual Entertainment)")
UNIQUE(FBSP, "QFusion / Warsow")
UNIQUE(RBSP, "SiN / Soldier of Fortune II / Star Wars Jedi Knight")
BASIC(2BSP, "DEPRECATED Quake Source Port format")
BASIC(IDQ1, "Quake Engine / Source Port")
BASIC(GSRC, "GoldSrc\nNOTE: Half-Life: Blue Shift flips the first 2 lump headers")
JMP_IBSP:
    switch (v) {
        case VERSION_IDQ2: REPORT_ID("Quake II Engine")
        case VERSION_IDQ3: REPORT_ID("Quake III Engine")
        case VERSION_RTCW: REPORT_ID("Return to Castle Wolfenstein")
        case VERSION_Q3DS: REPORT_X("Quake III Mod: Dark Salvation")
        case VERSION_COD1: REPORT_IW("Call of Duty / United Offensive")
        case VERSION_COD2: REPORT_IW("Call of Duty 2")
        case VERSION_COD4: REPORT_IW("Call of Duty: Modern Warfare")
        case VERSION_DAIK: REPORT_X("Daikatana")
        case VERSION_SOLD: REPORT_X("Soldier of Fortune")
        default: printf("Unknown Id Software / Infinity Ward .bsp (v%d)\n", v);
    }
    goto JMP_NEXT;
JMP_PBSV:
    printf("Xbox 360 ");
    BIG_ENDIAN;
JMP_VBSP:
    switch (v) {
        case VERSION_CRIM: REPORT_SOURCE("HL2 BETA [ILLEGAL]")
        case VERSION_VTMB: REPORT_SOURCE("Vampire: The Masqerade - Bloodlines")
        case VERSION_2007: REPORT_SOURCE("Orange Box")
        case VERSION_2013: REPORT_SOURCE("2013 SDK or L4D2 or Alien Swarm")
        case VERSION_XSDK: REPORT_SOURCE("Extended 2013 SDK")
        case VERSION_CSO2: REPORT_SOURCE("Counter-Strike: Online 2") /* NOTE: 2 eras (pre/post 2013) */
        case VERSION_DMMM: REPORT_SOURCE("Dark Mesiah of Might & Magic")  /* NOTE: SP & MP differ!*/
        default: printf("Unknown Source Engine .bsp (v%d)\n", v);
    }
    goto JMP_NEXT;
JMP_PBSr:
    printf("Xbox 360 ");
    BIG_ENDIAN;
JMP_rBSP:
    switch (v) {
        case VERSION_RER1: REPORT_TITAN("Titanfall / Titanfall: Online")
        case VERSION_R2TT: REPORT_TITAN("Titanfall 2 Tech Test")
        case VERSION_RER2: REPORT_TITAN("Titanfall 2")
        case VERSION_R5S0: REPORT_APEX("0-6")
        case VERSION_R5S7: REPORT_APEX("7")
        case VERSION_R5S8: REPORT_APEX("8-9 + 11.0 Depot")
        case VERSION_R5SA: REPORT_APEX("10")
        case VERSION_R5SB: REPORT_APEX("11")
        case VERSION_R5SC: REPORT_APEX("11.1 Depot")
        case VERSION_R5SD: REPORT_APEX("13")
        default: printf("Unknown Titanfall Engine .bsp (v%d)\n", v);
    }
    goto JMP_NEXT;
JMP_HELP:
    printf("Usage: %s [OPTIONS] FILE... \n", v[0]);
    printf("Identify the developer of a given .bsp file\n\n");
    printf("  -h, --help  display this help and exit\n");
JMP_KILL:
    return 0;

JMP_STRT:
    if (--c) goto JMP_HELP;
    for (; c > 0; --c) {
        printf("%s ", a[c]);
        f = fopen(a[c], "rb");
        if (!f) { printf("not found.\n"); continue; }
        READ
        switch(m) {
            CASE_MAGIC(2015)
            CASE_MAGIC(2PSB)
            CASE_MAGIC(BSP2)
            CASE_MAGIC(EF2_)
            CASE_MAGIC(RBSP)
            CASE_VERSION(IDT2)
            CASE_VERSION(GSRC)
            CASE_MAGIC(IBSP)
            CASE_MAGIC(VBSP)
            CASE_MAGIC(PSBV)
            CASE_MAGIC(rBSP)
            CASE_MAGIC(PSBr)
            default: printf("could not be indentified.\n");
        }
JMP_NEXT:
        fclose(f);  /* idk what to do w/ errors so just ignore them */
    }
    goto JMP_KILL;
}
