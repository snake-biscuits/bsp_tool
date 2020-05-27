#version 450 core
layout(location = 0) out vec4 outColour;

/* Vertex Data */
in vec3 position;
// in smooth vec3 normal;
// in vec2 albedoUV;

in vec4 vertexIndexColour;

void main()
{
	outColour = vertexIndexColour;
}
