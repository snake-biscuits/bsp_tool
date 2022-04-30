#version 300 es
layout(location = 0) in vec3 vertex_position;
layout(location = 1) in vec3 vertex_normal;
layout(location = 2) in vec3 vertex_colour;
layout(location = 3) in vec2 vertex_uv0;

uniform mat4 view_matrix;

out vec3 position;
out vec3 normal;
out vec3 colour;
out vec2 uv0;


void main() {
    position = vertex_position;
    normal = vertex_normal;
    colour = vertex_colour;
    uv0 = vertex_uv0;

    gl_Position = view_matrix * vec4(vertex_position, 1);
}

