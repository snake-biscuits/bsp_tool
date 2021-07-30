#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#ifndef FILESIZE_LIMIT // gcc watermark.c -DFILESIZE_LIMIT=1048576 -o watermark.exe
#define FILESIZE_LIMIT 1048576  // ~1MB
#endif

int main(int argc, char* argv[]) {
    if (argc != 2) {
        printf("Usage: %s FILE\nOutput: FILE.signed", argv[0]);
        return 1; }
    // read
    FILE* file = fopen(argv[1], "rb");
    char* buffer; buffer = (char*) malloc(FILESIZE_LIMIT);
    int filesize = fread(buffer, 1, FILESIZE_LIMIT, file);
    if (filesize == FILESIZE_LIMIT) {
        printf("%s is too large!\nMust be under %d bytes!\n", argv[1], FILESIZE_LIMIT);
        free(buffer); fclose(file);
        return 2; }
    // verify
    char file_magic[5] = "    ";
    memcpy(&file_magic, (char*) buffer, 4);
    file_magic[4] = '\0';
    if (!strcmp(file_magic, "VBSP")) {
        printf("%s in not a .bsp file!\n", argv[1]);
        free(buffer); fclose(file);
        return 3; }
    fclose(file);
    // sign
    int offset, length;  // PAKFILE_header
    memcpy(&offset, (char*) &buffer[648], 4);
    memcpy(&length, (char*) &buffer[652], 4);
    int addr = offset + length - 8;  // append to tail of XZP1 comment
    memcpy(&buffer[addr], (char*) "GET REKT", 8);
    strcat(argv[1], ".signed");
    // write
    file = fopen(argv[1], "wb");
    fwrite(buffer, 1, filesize, file);
    free(buffer); fclose(file);
    return 0;
}
