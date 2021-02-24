#version 300 es
layout(location = 0) out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec2 uv;


void main() {
    mediump vec4 ambient = vec4(0.15, 0.15, 0.15, 1);

    outColour = vec4(0.75, 0.75, 0.75, 1) + ambient;
}
