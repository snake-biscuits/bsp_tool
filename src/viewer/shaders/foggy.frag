#version 300 es
layout(location = 0) out mediump vec4 outColour;


in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;
in mediump vec2 uv0;

in highp vec4 gl_FragCoord;


void main() {
    mediump float Ka = 0.15;
    mediump vec3 sun = vec3(0.21, 0.93, -0.29);  // mp_box sun angles as a vector
    mediump float Kd = pow(2.0, abs(dot(normal, sun)));
    outColour = vec4(colour, 1) * min(Kd + Ka, 1.0);

    /* Apply Fog */
    // TODO: get fog settings as uniforms
    mediump vec4 fog_colour = vec4(1, 1, 1, 1);
    mediump float fog_depth = 32000.0;
    mediump float z = (gl_FragCoord.z / gl_FragCoord.w) / fog_depth;
    outColour = mix(outColour, fog_colour, z);
}
