#version 450 core
layout(location = 5) in vec3 vertexPosition;
//layout(location = 6) in vec3 vertexNormal;
//layout(location = 7) in vec2 vertexTexCoord;

uniform mat4 gl_ModelViewProjectionMatrix;

/* Vertex Data */
out vec3 position;
//out smooth vec3 normal;
//out vec2 albedoUV;

//out float fake_Kd;

void main()
{
    position = vertexPosition;
    //normal = vertexNormal;
    //albedoUV = vertexTexCoord;
	
	//fake_Kd = abs(normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3);
	
	gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1);
}
