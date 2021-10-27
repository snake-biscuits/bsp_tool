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

DUMMY != mkdir -p $(BIN_DIR)

.PHONY: all run


all: make_build_dir $(BIN_DIR)/test.exe $(BIN_DIR)/glview.exe

run: $(BIN_DIR)/glview.exe
	$(BIN_DIR)/glview.exe

# TODO: .o builds
# TODO: clean

# sketches
$(BIN_DIR)/test.exe: $(SRC_DIR)/test.cpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@

# OpenGL .bsp viewer
$(BIN_DIR)/glview.exe: $(SRC_DIR)/glview.cpp
	$(CC) $(CXXFLAGS) $(LDLIBS) $< -o $@ $(SDLFLAGS)
