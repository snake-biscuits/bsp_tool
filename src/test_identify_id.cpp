// g++ test_identify_id.cpp -o test_identify_id.exe
#include <iostream>

#include "identify_id.hpp"


int main() {
    std::string  string_IBSP ("IBSP");
    bool         is_IBSP = matchID(string_IBSP, IBSP);
    printf("bool(\"%s\" == %i) = %s\n", string_IBSP.c_str(), IBSP, is_IBSP ? "true" : "false");

    std::string  string_VBSP ("VBSP");
    bool         is_VBSP = matchID(string_VBSP, VBSP);
    printf("bool(\"%s\" == %i) = %s\n", string_VBSP.c_str(), VBSP, is_VBSP ? "true" : "false");

    std::string  string_rBSP ("rBSP");
    bool         is_rBSP = matchID(string_rBSP, rBSP);
    printf("bool(\"%s\" == %i) = %s\n", string_rBSP.c_str(), rBSP, is_rBSP ? "true" : "false");

    if ( !is_IBSP || !is_VBSP || !is_rBSP ) {
        return 1;
    }

    return 0;
};
