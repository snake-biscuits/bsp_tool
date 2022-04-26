#version 300 es
layout(location = 0) out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;
in mediump vec2 uv0;


void main() {
    /*
    mediump vec4 Ka = vec4(0.15, 0.15, 0.15, 1);
    mediump vec3 sun = vec3(.2, .3, .5);
    mediump float Kd = dot(normal, sun);
    outColour = vec4(Kd, Kd, Kd, 1) + Ka;
    */
    outColour = vec4(colour, 1);
}

