#version 450 core
layout(location = 0) out vec4 outColour;

/* Vertex Data */
in vec3 position;
in smooth vec3 normal;
in vec2 texUV;
in vec2 lightUV;
in vec3 reflectivityColour;

in int vertexIndex; // gl_VertexID

void main()
{
	// vec4 Ka = vec4(0.25, 0.25, 0.25, 1); // Ka = ambient
	// outColour = vec4(texUV, 1, 1) * Ka;
	
	/* Vertex Scrambling Check */
	float A = vertexIndex >> 24;
	float B = (vertexIndex >> 16) & 0xFF;
	float G = (vertexIndex >> 8) & 0xFF;
	float R = vertexIndex & 0xFF;
	outColor = vec4(R / 255, G / 255, B / 255, A / 255); // Index encoded as colour
}
