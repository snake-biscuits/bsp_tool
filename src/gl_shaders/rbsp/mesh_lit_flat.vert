#version 300 es
layout(location = 0) in vec3 vertex_position;  // VERTEX[i]
layout(location = 1) in vec3 vertex_normal;    // VERTEX_NORMAL[j]
layout(location = 2) in vec2 vertex_uv_albedo;
// vertex_uv_lightmap?
// 20 unknown bytes

uniform mat4 view_matrix;

out vec3 position;
out vec3 normal;
out vec2 uv_albedo;


void main() {
    position = vertex_position;
    normal = vertex_normal;
    uv_albedo = vertex_uv_albedo;

    gl_Position = view_matrix * vec4(vertex_position, 1);
}
