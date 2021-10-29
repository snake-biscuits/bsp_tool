CC       := g++
CXXFLAGS := --std=c++17 -Wall
LDLIBS   := -lstdc++fs

SDLFLAGS := -lGL `sdl2-config --cflags --libs`

ifeq ($(OS),Windows_NT)
    CC   := x86_64-w64-mingw32-g++
    # NOTE: may need alternate SDLFLAGS here too
endif

DUMMY != mkdir -p build

.PHONY: all run


all: build/lump_names.exe build/glview.exe

run: build/glview.exe
	build/glview.exe

# TODO: .o builds
# TODO: clean

build/lump_names.exe: src/lump_names.cpp src/bsp_tool.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

# OpenGL .bsp viewer
# NOTE: untested on Windows
build/glview.exe: src/glview.cpp src/bsp_tool.hpp src/respawn_entertainment/meshes.hpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)
