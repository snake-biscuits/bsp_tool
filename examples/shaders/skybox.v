#version 450 core
layout(location = 0) in vec3 vertexPosition;

uniform mat4 gl_ModelViewProjectionMatrix;

out vec3 position;

void main()
{
    position = vertexPosition;
	gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1);
}
