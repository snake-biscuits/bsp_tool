// quake_vertices.c
#include <errno.h>
#include <stdio.h>
#include <stdlib.h>

#include "quake_bsp.h"


enum { LUMP_VERTICES = 3 };
typedef struct { float x, y, z; } Vertex;


int main(int argc, char* argv[]) {
    FILE           *bsp_file;
    QuakeBspHeader  bsp_header;
    int             errsv;
    Vertex         *vertex_lump;
    unsigned int    vertex_lump_len;
    /* Handle arguments */
    if (argc != 2) {
        fprintf(stderr, "Expected use: %s FILE.BSP\n", argv[0]);
        return 0;
    }
    /* Open FILE.BSP */
    bsp_file = fopen(argv[1], "rb");
    if (!bsp_file) {
        errsv = errno;
        fprintf(stderr, "Couldn't open %s\n", argv[1]);
        return 1;
    }
    /* Read FILE.BSP lump data */
    #define BSP_ASSERT(cond, msg) if (!(cond)) { fprintf(stderr, msg, argv[1]); return 1; }
    fread(&bsp_header, sizeof(QuakeBspHeader), 1, bsp_file);
    BSP_ASSERT(bsp_header.version == BSP_VERSION_QUAKE, "%s is not a Quake .bsp!\n")
    vertex_lump_len = bsp_header.lump[LUMP_VERTICES].length / sizeof(Vertex);
    vertex_lump = malloc(vertex_lump_len);
    fseek(bsp_file, bsp_header.lump[LUMP_VERTICES].offset, SEEK_SET);
    fread(&vertex_lump[0], sizeof(Vertex), vertex_lump_len, bsp_file);
    #undef BSP_ASSERT
    /* Close FILE.BSP */
    errno = 0;
    if (!fclose(bsp_file) && errno) {
        errsv = errno;
        fprintf(stderr, "Encountered an error closing: %s; errno = %d\n", argv[1], errsv);
        return 1;
    }
    /* Print all vertices in FILE.BSP */
    printf("%s has %d vertices:\n", argv[1], vertex_lump_len);
    for (int i=0; i<vertex_lump_len; i++) {
        Vertex v = vertex_lump[i];
        printf("vertex[%d] = (%.3f, %.3f, %.3f)\n", i, v.x, v.y, v.z);
    }

    return 0;
}
