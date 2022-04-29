#version 450 core
layout(location = 0) out vec4 outColour;


/* Vertex Data */
in vec3 position;
in smooth vec3 normal;
in vec2 albedoUV;

in float fakeKd;
in vec3 vertexIndexColour;

in vec4 gl_FragCoord;


void main() {
	vec4 Ka = vec4(0.5, 0.5, 0.5, 1);

	// float stripe = mod((albedoUV.x + albedoUV.y) / 64.0, 1.0);
	// stripe = (stripe > 0.5 ? 1.0 : 0.25);

	outColour = vec4(vertexIndexColour, 1) * min(fakeKd + Ka, 1);  // * stripe;

    /* Apply Fog */
	// float z = (gl_FragCoord.z / gl_FragCoord.w) / 32000.0;
	// outColour = mix(outColour, vec4(1, 1, 1, 1), z);

}
