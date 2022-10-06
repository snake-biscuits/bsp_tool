#version 300 es
layout(location = 0) out highp vec4 outColour;

in highp vec3 position;
in highp vec3 normal;
in highp vec3 colour;
in highp vec2 uv0;

// TODO: uniform highp vec3 sun;  // collect from LevelInfo


void main() {
    highp float Ka = 0.15;
    highp vec3 sun = vec3(0.21, 0.93, -0.29);  // mp_box sun angles as a vector
    highp float Kd = pow(2.0, abs(dot(normal, sun)));

    outColour = vec4(colour, 1) * min(Kd + Ka, 1.0);
}

