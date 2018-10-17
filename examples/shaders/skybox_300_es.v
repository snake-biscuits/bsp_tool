#version 300 es
in vec3 vertexPosition;

uniform mat4 ProjectionMatrix;

out mediump vec3 position;

void main()
{
    position = vertexPosition;
    gl_Position = (ProjectionMatrix * vec4(position, 1)).xyww;
}
