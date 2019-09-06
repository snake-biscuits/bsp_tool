#version 450 core
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexTexCoord;
layout(location = 3) in vec2 vertexLightCoord;
layout(location = 4) in vec3 vertexColour;

uniform mat4 gl_ModelViewProjectionMatrix;

out vec3 position;
out smooth vec3 normal;
out vec2 texUV;
out vec2 lightUV;
out vec3 reflectivityColour;

void main()
{
    position = vertexPosition;
    normal = vertexNormal;
    texUV = vec2(vertexTexCoord.x, -vertexTexCoord.y);
    lightUV = vertexLightCoord;
	reflectivityColour = vertexColour;
	
	gl_Position = gl_ModelViewProjectionMatrix * vec4(vertexPosition, 1);
}