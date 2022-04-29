#version 450 core
layout(location = 0) out vec4 outColour;

/* Vertex Data */
in vec3 position;
in smooth vec3 normal;
in vec2 texUV;
in vec2 lightUV;
in vec3 reflectivityColour;

in vec4 vertexIndexColour;

void main()
{
	// vec4 Ka = vec4(0.25, 0.25, 0.25, 1); // Ka = ambient
	// outColour = vec4(texUV, 1, 1) * Ka;
	
	outColour = vec4(vertexIndexColour.rgb, 1);
	
}
