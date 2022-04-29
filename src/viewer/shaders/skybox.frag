#version 450 core
layout(location = 0) out vec4 outColour;

in vec3 position;

uniform samplerCube skybox;

void main()
{
	outColour = texture(skybox, position);
}
