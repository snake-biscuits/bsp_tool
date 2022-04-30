CC       := g++
CXXFLAGS := --std=c++17 -Wall
LDLIBS   := -lstdc++fs

SDLFLAGS := -lGLEW -lGL `sdl2-config --cflags --libs`

R1_MAPS_DIR  := /media/bikkie/Sandisk/Respawn/r1/maps
R1O_MAPS_DIR := /media/bikkie/Sandisk/Respawn/r1o/maps
R2_MAPS_DIR  := /media/bikkie/Sandisk/Respawn/r2/maps
R5_DIR       := /media/bikkie/Sandisk/Respawn/r5/maps

TESTMAP := /home/bikkie/Documents/Maps/mp_switchback.bsp

ifeq ($(OS),Windows_NT)
    # NOTE: if compiling for Windows, use MSYS2 / MINGW64
    # DEPENDENCIES:
    # -- mingw-w64-x86_64-glew
    # -- mingw-w64-x86_64-glm
    # -- mingw-w64-x86_64-mesa
    # -- mingw-w64-x86_64-SDL2
    # TODO: figure out standalone Windows builds
    CC       := x86_64-w64-mingw32-g++
    SDLFLAGS := -lm -mwindows -mconsole -lopengl32 -lglew32 `sdl2-config --cflags --libs`

    R1_MAPS_DIR  := /E/Mod/Titanfall/maps
    R1O_MAPS_DIR := /E/Mod/TitanfallOnline/maps
    R2_MAPS_DIR  := /E/Mod/Titanfall2/maps
    R5_DIR       := /E/Mod/ApexLegends

    TESTMAP := $(R1_MAPS_DIR)/mp_angel_city.bsp
endif

# TESTMAP := $(R1_MAPS_DIR)/mp_runoff.bsp
# TESTMAP := $(R1O_MAPS_DIR)/mp_box.bsp

DUMMY != mkdir -p build

.PHONY: all run debug


all: build/lump_names.exe build/viewer.exe

run: build/viewer.exe
	build/viewer.exe $(TESTMAP)

debug:
	$(CC) $(CXXFLAGS) -ggdb $(LDLIBS) src/viewer/main.cpp -o build/viewer.exe $(SDLFLAGS)
	gdb --args build/viewer.exe $(TESTMAP) -ex run -ex bt

# TODO: .o builds
# TODO: clean

build/lump_names.exe: src/lump_names.cpp src/bsp_tool.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

build/viewer.exe: src/viewer/main.cpp src/bsp_tool.hpp src/viewer/camera.hpp src/common.hpp src/respawn_entertainment/meshes.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)
