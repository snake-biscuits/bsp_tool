CC       := g++
CXXFLAGS := --std=c++17 -Wall
LDLIBS   := -lstdc++fs

SDLFLAGS := -lGLEW -lGL `sdl2-config --cflags --libs`
R1_MAPS_DIR  := /media/bikkie/Sandisk/Respawn/r1/maps
R1O_MAPS_DIR := /media/bikkie/Sandisk/Respawn/r1o/maps
R2_MAPS_DIR  := /media/bikkie/Sandisk/Respawn/r2/maps
R5_DIR       := /media/bikkie/Sandisk/Respawn/r5/maps

ifeq ($(OS),Windows_NT)
    # NOTE: if compiling for Windows, use MSYS2 / MINGW64
    # -- you will need to copy some .dlls to /build; ntldd is helpful for this
    CC       := x86_64-w64-mingw32-g++
    SDLFLAGS := -lm -Wl,-subsystem,windows -lopengl32 `sdl2-config --cflags --libs`
    R1_MAPS_DIR  := /e/Mod/Titanfall/maps
    R1O_MAPS_DIR := /e/Mod/TitanfallOnline/maps
    R2_MAPS_DIR  := /e/Mod/Titanfall2/maps
    R5_DIR       := /e/Mod/ApexLegends/maps
endif

# TESTMAP := $(R1_MAPS_DIR)/mp_colony.bsp
# TESTMAP := $(R1O_MAPS_DIR)/mp_box.bsp
# TESTMAP := $(R1O_MAPS_DIR)/mp_npe.bsp
TESTMAP := /home/bikkie/Documents/Maps/mp_switchback.bsp

DUMMY != mkdir -p build

.PHONY: all run debug


all: build/lump_names.exe build/glview.exe

run: build/glview.exe
	build/glview.exe $(TESTMAP)

debug:
	$(CC) $(CXXFLAGS) -ggdb $(LDLIBS) src/glview.cpp -o build/glview.exe $(SDLFLAGS)
	gdb --args build/glview.exe $(TESTMAP)

# TODO: .o builds
# TODO: clean

build/lump_names.exe: src/lump_names.cpp src/bsp_tool.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

# OpenGL .bsp viewer
# NOTE: untested on Windows (not compiling)
build/glview.exe: src/glview.cpp src/bsp_tool.hpp src/camera.hpp src/common.hpp src/respawn_entertainment/meshes.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)
