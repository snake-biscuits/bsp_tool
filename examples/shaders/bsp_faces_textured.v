#version 450 core
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexTexCoord;
layout(location = 3) in vec2 vertexLightCoord;

uniform mat3 gl_NormalMatrix; /*Causes view angle to affect normal*/
uniform mat4 gl_ModelViewProjectionMatrix;

out vec3 position;
out smooth vec3 normal;
out vec2 texUV;
out vec2 lightUV;


void main()
{
    position = vertexPosition;
    normal = gl_NormalMatrix * vertexNormal;
    texUV = vertexTexCoord;
    lightUV = vertexLightCoord;

	gl_Position = gl_ModelViewProjectionMatrix * vec4(vertexPosition, 1);
}
