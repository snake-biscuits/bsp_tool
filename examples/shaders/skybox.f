#version 450 core
layout(location = 0) out vec4 outColour;

in vec3 position;

uniform samplerCube skybox;

void main()
{
    /* Convert to Y-UP because Pixar's Renderman did cubemaps first*/
    vec3 cubeVector = vec3(position.x, -position.z, position.y);
	outColour = texture(skybox, cubeVector);
}
