#include <iostream>


// NOTE: endianness matters!
const int IBSP = 'I' + ('B' << 8) + ('S' << 16) + ('P' << 24);  // Id Software
const int VBSP = 'V' + ('B' << 8) + ('S' << 16) + ('P' << 24);  // Valve Software
const int rBSP = 'r' + ('B' << 8) + ('S' << 16) + ('P' << 24);  // Respawn Entertainment

/* pointers: quick reference */
// int* X;      // declare int pointer X
// *X;          // get value at location of pointer X
// &X;          // get a pointer to X
// (char*) &X;  // reinterpret type at pointer location &X to type char*


bool matchID(std::string id, int id_checksum) {
    if (id.length() != 4) return false;
    int* id_as_int = reinterpret_cast<int*>(const_cast<char*>(id.c_str()));
    return (*id_as_int == id_checksum);
};

