#version 300 es
in vec3 vertexPosition;

uniform mat4 mvpMatrix;

out mediump vec3 position;

void main()
{
    position = vertexPosition;
    gl_Position = mvpMatrix * vec4(position, 1);
}
