#version 450 core
layout(location = 0) in vec3 vertexPosition;

uniform mat4 gl_ModelViewProjectionMatrix;

out vec3 position;
out vec2 uv;

void main()
{
    position = vertexPosition;
    uv = clamp(vertexPosition.xy, 0, 1);
	
	gl_Position = gl_ModelViewProjectionMatrix * vec4(vertexPosition, 1);
}