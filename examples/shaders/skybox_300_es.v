#version 300 es
in vec3 vertexPosition;

uniform mat4 mvpMatrix;

out mediump vec3 position;

void main()
{
    /* Convert to Y-UP because Pixar's Renderman did cubemaps first*/
    position = vec3(vertexPosition.y, -vertexPosition.z, vertexPosition.x);
    gl_Position = mvpMatrix * vec4(vertexPosition, 1);
}
