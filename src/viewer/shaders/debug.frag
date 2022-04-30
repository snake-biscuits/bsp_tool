#version 300 es
layout(location = 0) out mediump vec4 outColour;


in mediump vec3 position;
in mediump vec3 normal;
in mediump vec3 colour;
in mediump vec2 uv0;

// in vec4 gl_FragCoord;


void main() {
    mediump vec4 Ka = vec4(0.5, 0.5, 0.5, 1);
    mediump vec3 sun = vec3(0.65, 0.35, -0.15);
    mediump Kd = abs(dot(normal, sun));
    // mediump float stripe = mod((uv0.x + uv0.y) / 64.0, 1.0);
    // stripe = (stripe > 0.5 ? 1.0 : 0.25);
    outColour = vec4(colour, 1) * min(Kd + Ka, 1);  // * stripe;

    /* Apply Fog */
    // mediump float fog_colour = vec4(1, 1, 1, 1);
    // mediump float fog_depth = 32000.0;
    // mediump float z = (gl_FragCoord.z / gl_FragCoord.w) / fog_depth;
    // outColour = mix(outColour, fog_colour, z);

}
