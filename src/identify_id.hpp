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


// g++ identify_id.hpp -o test_identify_id.exe -DTEST
#ifdef TEST
int main() {
    std::string  string_IBSP ("IBSP");
    bool         is_IBSP = matchID(string_IBSP, IBSP);
    printf("bool(%s == %i) = %s", string_IBSP.c_str(), IBSP, is_IBSP ? "true" : "false");

    std::string  string_VBSP ("VBSP");
    bool         is_VBSP = matchID(string_VBSP, VBSP);
    printf("bool(%s == %i) = %s", string_VBSP.c_str(), VBSP, is_VBSP ? "true" : "false");

    std::string  string_rBSP ("rBSP");
    bool         is_rBSP = matchID(string_rBSP, rBSP);
    printf("bool(%s == %i) = %s", string_rBSP.c_str(), rBSP, is_rBSP ? "true" : "false");

    if ( !is_IBSP || !is_VBSP || !is_rBSP ) {
        return 1;
    }

    return 0;
};
#endif
