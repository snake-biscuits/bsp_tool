# NOTE: this builds the experiemental C++17 implementation
# super basic and missing most of the python implementation's features!
SRC_DIR := src
BIN_DIR := build

ifdef OS  # Microsoft Windows
    CC   := x86_64-w64-mingw32-g++
else
    CC   := g++
endif
CXXFLAGS := --std=c++17 -Wall
LDLIBS   := -lstdc++fs

SDLFLAGS := -lGL `sdl2-config --cflags --libs`

.PHONY: all make_build_dir


all: make_build_dir $(BIN_DIR)/test.exe $(BIN_DIR)/glview.exe

make_build_dir:
	mkdir -p build


# TODO: .o builds
# TODO: clean

# sketches
$(BIN_DIR)/test.exe: $(SRC_DIR)/test.cpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

# OpenGL .bsp viewer
$(BIN_DIR)/glview.exe: $(SRC_DIR)/glview.cpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)
