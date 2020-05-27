#version 450 core
layout(location = 0) in vec3 vertexPosition;
layout(location = 1) in vec3 vertexNormal;
layout(location = 2) in vec2 vertexTexCoord;
layout(location = 3) in vec2 vertexLightCoord;
layout(location = 4) in vec3 vertexColour;

uniform mat3 gl_NormalMatrix; /*Causes view angle to affect normal*/
uniform mat4 gl_ModelViewProjectionMatrix;

/* Vertex Data */
out vec3 position;
out smooth vec3 normal;
out vec2 texUV;
out vec2 lightUV;
out vec3 reflectivityColour;

out float fake_Kd;
in int gl_VertexID;
out int vertexIndex;

void main()
{
    position = vertexPosition;
    normal = vertexNormal;
    texUV = vec2(vertexTexCoord.x, -vertexTexCoord.y);
    lightUV = vertexLightCoord;
	reflectivityColour = vertexColour;
	
	fake_Kd = abs(normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3);
	vertexIndex = gl_VertexID;
	
	gl_Position = gl_ModelViewProjectionMatrix * vec4(vertexPosition, 1);
}
