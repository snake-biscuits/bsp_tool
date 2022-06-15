// quake_bsp.h
#include <stdint.h>

#define BSP_VERSION_QUAKE  29

typedef struct {
    uint32_t  offset;
    uint32_t  length;
} QuakeLumpHeader;

typedef struct {
    uint32_t         version;  /* BSP_VERSION_QUAKE (29) */
    QuakeLumpHeader  lump[15];
} QuakeBspHeader;

