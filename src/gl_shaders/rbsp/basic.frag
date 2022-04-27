#version 300 es
layout(location = 0) out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;  // why is it blue!?
in mediump vec2 uv0;


void main() {
    mediump float Ka = 0.25;
    mediump vec3 sun = vec3(0.2, 0.3, 0.5);
    mediump float Kd = dot(normal, sun);
    
    outColour = vec4(Kd, Kd, Kd, 1) + vec4(Ka, Ka, Ka, 1);
    outColour = outColour * vec4(colour, 1);
}

