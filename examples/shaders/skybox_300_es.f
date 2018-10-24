#version 300 es
out mediump vec4 outColour;

in mediump vec3 position;

uniform samplerCube skybox;

void main()
{
    /* Convert to Y-UP because Pixar's Renderman did cubemaps first*/
    mediump vec3 cubeVector = vec3(position.x, -position.z, position.y);
	outColour = texture(skybox, cubeVector);
    // outColour = vec4(1, 1, 1, 1);
}
