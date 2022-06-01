# `.bsp` file basics


## Structure

`.bsp` files usually have a file header containing the following information
 - version identifier
 - map revision (optional)
 - lump headers
   * offset
   * length
   * other meta-data

Some variants have a different order but at the very least the following should be present:
 - format version
 - lump headers
   * offset
   * length

```C
// quake_bsp.h
struct QuakeLumpHeader {
    uint32_t  offset;
    uint32_t  length;
};

struct QuakeBspHeader {
    uint32_t         version;  // 29
    QuakeLumpHeader  lump[15];
};
```


## Lumps

Lumps are the chunks of the file pointed at by bsp headers. They come in 2 forms:
    1. Array of Type
    2. Sequence of raw byte data
Most lumps are of the first form. These lumps hold data like rendered vertices.
The second form is employed for more complex systems, such as entity data & visibility trees

```C
// quake_vertices.c
#include <stdio.h>
#include <stdlib.h>

#include "quake_bsp.h"


enum { LUMP_VERTICES = 3; };
struct Vertex { float x, y, z; };


int main(int argc, char* argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Expected use: %s FILE.BSP\n", argv[0]);
        return -1;
    }

    FILE            bsp_file;
    QuakeBspHeader  bsp_header;
    Vertex*         vertex_lump;
    unsigned int    vertex_lump_len;
    
    bsp_file = fopen(argv[1], "rb");
    if (!bsp_file) {
        fprintf(stderr, "Couldn't open %s\n", argv[1]);
        return -2;
    }

    fread(&bsp_header, sizeof(QuakeBspHeader), 1, bsp_file);
    // TODO: verify bsp_header != NULL and bsp_header.version == 29
    vertex_lump_len = bsp_header.lump[LUMP_VERTICES].length / sizeof(Vertex);
    vertex_lump = malloc(vertex_lump_len);
    fseek(bsp_file, bsp_header.lump[LUMP_VERTICES].offset, SEEK_SET);
    fread(&vertex_lump[0], sizeof(Vertex), vertex_lump_len, bsp_file)
    if (!fclose(bsp_file)) {
        fprintf("Encountered an error closing: %s\n", argv[1]);
        return errno;
    }

    printf("%s has %d vertices:\n", argv[1], vertex_lump_len);
    for (int i=0; i<vertex_lump_len; i++) {
        Vertex v = vertex_lump[i];
        printf("vertex[%d] = {%.3f, %.3f, %.3f}\n", i, v.x, v.y, v.z);
    }

    return 0;
}
```


## Format History

The `.bsp` file format as it is known publically began with Quake (1996).
`.bsp` stands for Binary Space Partition
Binary Space Partioning is a method for optimising rendering developed by the US AIR FORCE in 1969[^1]
Use of a Binary Space Partition allows a renderer to only render what is possible to be seen from a given position in the level

## References

 [^1]: [STUDY FOR APPLYING COMPUTER-GENERATED IMAGES TO VISUAL SIMULATION](https://apps.dtic.mil/sti/citations/AD0700375)
