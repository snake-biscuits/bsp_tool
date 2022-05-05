#pragma once
#include <GL/gl.h>  // -lGL

#include "../common.hpp"


#define SET_RENDERVERTEX_ATTRIBS \
    glEnableVertexAttribArray(0); \
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, position)); \
    glEnableVertexAttribArray(1); \
    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, normal)); \
    glEnableVertexAttribArray(2); \
    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, colour)); \
    glEnableVertexAttribArray(3); \
    glVertexAttribPointer(3, 2, GL_FLOAT, GL_FALSE, sizeof(RenderVertex), (void*) offsetof(RenderVertex, uv));


struct Span {
    unsigned int start;
    unsigned int length;
};


struct RenderVertex {
    Vector    position;
    Vector    normal;
    float     colour[3];
    Vector2D  uv;
};


struct RenderObject {
    /* Buffer data */
    unsigned int  vertex_count;
    RenderVertex *vertices;  // always allocate w/ `new`
    unsigned int  index_count;
    unsigned int *indices;  // always allocate w/ `new`
    unsigned int  child_count;
    Span         *children;
    /* Shader & Buffer handles */
    GLuint        vertex_buffer;
    GLuint        index_buffer;
    GLuint        shader_program;

    /* Methods */
    RenderObject() {}
    ~RenderObject() {
        delete[] vertices;
        delete[] indices;
    }
};

