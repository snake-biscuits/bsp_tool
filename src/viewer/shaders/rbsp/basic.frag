#version 300 es
layout(location = 0) out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;
in mediump vec2 uv0;


void main() {
    mediump float Ka = 0.15;
    mediump vec3 sun = vec3(0.21, 0.93, -0.29);  // mp_box sun angles as approx normalised vector
    mediump float Kd = abs(dot(normal, sun)) * (1.0 - Ka);
    
    outColour = vec4(colour, 1) * (Kd + Ka);
}

