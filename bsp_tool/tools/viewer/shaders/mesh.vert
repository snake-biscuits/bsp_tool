#version 300 es
layout(location = 0) in vec3 vertex_position;
layout(location = 1) in vec3 vertex_normal;
layout(location = 2) in vec3 vertex_uv;

uniform mat4 view_matrix;

out vec3 position;
out vec3 normal;
out vec2 uv;


void main() {
    position = vertex_position;
    normal = vertex_normal;
    uv = vertex_uv;

    gl_Position = view_matrix * vec4(vertex_position, 1);
}
