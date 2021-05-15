#version 450 core
layout(location = 0) in vec3 vertexPosition;

uniform mat4 gl_ModelViewProjectionMatrix;

out vec3 position;

void main()
{
    /* Convert to Y-UP because Pixar's Renderman did cubemaps first*/
    position = vec3(vertexPosition.x, -vertexPosition.z, vertexPosition.y);;
	gl_Position = gl_ModelViewProjectionMatrix * vec4(vertexPosition, 1);
}
