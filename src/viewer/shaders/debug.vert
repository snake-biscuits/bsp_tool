#version 300 es
layout(location = 0) in mediump vec3 vertex_position;
layout(location = 1) in mediump vec3 vertex_normal;
// layout(location = 2) in mediump vec3 vertex_colour;
layout(location = 3) in mediump vec2 vertex_uv0;


uniform mediump mat4 view_matrix;
uniform highp int vertex_count;

out mediump vec3 position;
out mediump vec3 normal;
out mediump vec3 colour;
out mediump vec2 uv0;


// Python colorsys.hsv_to_rgb as GLSL
vec3 int_to_rgb(int integer) {
    // base colour
    mediump float hue = float(integer) / float(vertex_count) + 0.66;  // starts at deep blue
    mediump float saturation = 0.5;
    mediump float value = 0.0;
    // hue shift
    highp int i = int(hue * 6.0);
    mediump float f = (hue * 6.0) - float(i);
    // NOTE: these could all be constants if saturation never changes
    mediump float p = (1.0 - saturation);
    mediump float q = (1.0 - saturation * f);
    mediump float t = (1.0 - saturation * (1.0 - f));
    switch (i % 6) {
        case 0:
            return vec3(value, t, p);
        case 1:
            return vec3(q, value, p);
        case 2:
            return vec3(p, value, t);
        case 3:
            return vec3(p, q, value);
        case 4:
            return vec3(t, p, value);
        case 5:
            return vec3(value, p, q);
    }
}


void main() {
    position = vertex_position;
    normal = vertex_normal;
    colour = int_to_rgb(gl_VertexID);
    // vec3 desaturation_factor = vec3(0.3, 0.6, 0.1);
    // float d = dot(desaturation_factor, vertexIndexColour);
    // colour = vec3(d, d, d);
    uv0 = vertex_uv0;

    gl_Position = view_matrix * vec4(position, 1);
}
