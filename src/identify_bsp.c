/* C89 (ANSI C) COMPATIBLE! */
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "identify_bsp.h"


/* Utilities */
#define BASIC(x, y)  JMP_##x: printf(y "\n"); goto JMP_NEXT;
#define CONFIRM(x)  if (v!=x) fprintf(stderr, "\tWARNING: unexpected .bsp version (v%d; expected v%d)\n", v, x);
#define UNIQUE(x, y)  JMP_##x: printf(y "\n"); CONFIRM(VERSION_##x); goto JMP_NEXT;
/* ^ expand jump defs first ^ */
#define ENDIAN_FLIP  v = MAGIC(v >> 24, v >> 16 & 0xFF, v >> 8 & 0xFF, v & 0xFF);
#define CASE_X(x, y)  case x##_##y: goto JMP_##y;
#define CASE_MAGIC(x)  CASE_X(MAGIC, x)
#define CASE_VERSION(x)  CASE_X(VERSION, x)
#define CHAR(x, y)  ((x >> y * 8) & 0xFF)
#define IN_RANGE(x, y, z)  (x >= y && x <= z)
#define MAGIC_CHARS  CHAR(m, 0), CHAR(m, 1), CHAR(m, 2), CHAR(m, 3)
#define READ_X(x)  fread(x, sizeof(uint32_t), 1, f);
#define READ  READ_X(&m) READ_X(&v)
#define REPORT_X(x)  printf(x "\n"); break;
#define REPORT_ID(x)  REPORT_X("Id Software: " x)
#define REPORT_IW(x)  REPORT_X("Infinity Ward: " x)
#define REPORT_SOURCE(x)  REPORT_X("Source Engine: " x " branch")
#define REPORT_TITAN(x)  REPORT_X("Titanfall Engine: " x)
#define REPORT_APEX(x)  REPORT_X("Apex Legends (Season " x ")")
#define REPORT_WARN  fprintf(stderr, "\tWARNING: %c%c%c%c v%d identifies multiple branches\n", MAGIC_CHARS, v);
#define SAFE(x) (IN_RANGE(x, 'a', 'z') || IN_RANGE(x, 'A', 'Z') || IN_RANGE(x, '0', '9') || (x == '!'))


int main(int c, char** a) {
    FILE     *f;
    uint32_t  m, v;

    goto JMP_STRT;
    /* ONE VERSION */
    UNIQUE(EALA, "Medal of Honor: Allied Assault - Breakthrough (by EA Los Angeles)")
    UNIQUE(EF2_, "Star Trek: Elite Force II (by Ritual Entertainment)")
    UNIQUE(FBSP, "QFusion / Warsow")
    UNIQUE(RBSP, "SiN / Soldier of Fortune II / Star Wars Jedi Knight")  /* TODO: REPORT_WARN 3-way branch conflict */
    /* NO VERSION */
    BASIC(2PSB, "DEPRECATED Quake Source Port")
    BASIC(BSP2, "ReMakeQuake")
    BASIC(GSRC, "GoldSrc")  /* TODO: REPORT_WARN overlap w/ Half-Life: Blue Shift */
    BASIC(JBNF, "James Bond 007: Nightfire")
    BASIC(IDQ1, "Quake Engine")
JMP_2015:
    switch (v) {
        case VERSION_2015: REPORT_X("Medal of Honor: Allied Assault (by 2015 Inc.)")
        case VERSION_DEMO: REPORT_X("Medal of Honor: Allied Assault [Demo] (by 2015 Inc.)")
    }
    goto JMP_NEXT;
JMP_FAKK:
    switch (v) {
        case VERSION_FAKK: REPORT_X("Heavy Metal F.A.K.K 2")
        case VERSION_ALIC: REPORT_X("American McGee's Alice")
    }
    goto JMP_NEXT;
JMP_IBSP:
    switch (v) {
        case VERSION_IDQ2: REPORT_ID("Quake II Engine")
        case VERSION_IDQ3: REPORT_WARN
                           REPORT_ID("Quake III Engine or Soldier of Fortune")
        case VERSION_RTCW: REPORT_ID("Return to Castle Wolfenstein")
        case VERSION_Q3DS: REPORT_X("Quake III Mod: Dark Salvation")
        case VERSION_COD1: REPORT_IW("Call of Duty / United Offensive")
        case VERSION_COD2: REPORT_IW("Call of Duty 2")
        case VERSION_COD4: REPORT_IW("Call of Duty: Modern Warfare")
        case VERSION_DAIK: REPORT_X("Daikatana")
        default: printf("Unknown Id Software / Infinity Ward .bsp (v%d)\n", v);
    }
    goto JMP_NEXT;
JMP_PSBV:
    printf("Xbox 360 ");
    ENDIAN_FLIP;
JMP_VBSP:
    switch (v) {
        case VERSION_CRIM: REPORT_SOURCE("HL2 BETA [ILLEGAL]")
        case VERSION_VTMB: REPORT_SOURCE("Vampire: The Masqerade - Bloodlines")
        case VERSION_2007: REPORT_WARN
                           REPORT_SOURCE("Orange Box or Left4Dead")
        case VERSION_2013: REPORT_WARN
                           REPORT_SOURCE("2013 SDK or L4D2 or Alien Swarm")
        case VERSION_XSDK: REPORT_SOURCE("Extended 2013 SDK")
        case VERSION_CONT: REPORT_SOURCE("Contagion")
        case VERSION_CSO2: REPORT_WARN
                           REPORT_SOURCE("Counter-Strike: Online 2 (2013 or 2018)")
        case VERSION_DMMM: REPORT_WARN
                           REPORT_SOURCE("Dark Mesiah of Might & Magic (SP or MP)")
        default: printf("Unknown Source Engine .bsp (v%d)\n", v);
    }
    goto JMP_NEXT;
JMP_PSBr:
    printf("Xbox 360 ");
    ENDIAN_FLIP;
JMP_rBSP:
    switch (v) {
        case VERSION_R1RE: REPORT_TITAN("Titanfall / Titanfall: Online")
        case VERSION_R2TT: REPORT_TITAN("Titanfall 2 Tech Test")
        case VERSION_R2RE: REPORT_TITAN("Titanfall 2")
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
    printf("Usage: %s [OPTIONS] FILE... \n", a[0]);
    printf("Identify the developer of a given .bsp file\n\n");
    printf("  -h, --help  display this help and exit\n");
JMP_KILL:
    return 0;

JMP_STRT:
    if (!--c) goto JMP_HELP;
    for (; c > 0; --c) {  /* NOTE: args processed in reverse order */
        if (a[c][0] == '-') {
            if (!strcmp(a[c], "-h") || !strcmp(a[c], "--help"))
                goto JMP_HELP;
            else {
                fprintf(stderr, "unknown option: %s\n", a[c]);
                goto JMP_HELP;
            }
        }
        printf("%s\n\t", a[c]);
        f = fopen(a[c], "rb");
        if (!f) { printf("not found.\n"); continue; }
        READ
        switch(m) {
            CASE_MAGIC(2015)
            CASE_MAGIC(2PSB)
            CASE_MAGIC(BSP2)
            CASE_MAGIC(EALA)
            CASE_MAGIC(EF2_)
            CASE_MAGIC(FAKK)
            CASE_MAGIC(FBSP)
            CASE_MAGIC(IBSP)
            CASE_MAGIC(PSBV)
            CASE_MAGIC(RBSP)
            CASE_MAGIC(rBSP)
            CASE_MAGIC(PSBr)
            CASE_MAGIC(VBSP)
            CASE_VERSION(GSRC)
            CASE_VERSION(IDQ1)
            CASE_VERSION(JBNF)
            default:
                fprintf(stderr, "Could not be identified.\n");
                if (SAFE(CHAR(m , 0)) && SAFE(CHAR(m, 1)) && SAFE(CHAR(m, 2)) && SAFE(CHAR(m, 3)))
                    printf("\tMAGIC = %c%c%c%c, VERSION = %d\n", MAGIC_CHARS, v);

        }
JMP_NEXT:
        fclose(f);  /* idk what to do w/ errors so just ignore them */
    }
    goto JMP_KILL;
}
