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
in int gl_VertexID;
out vec3 vertexIndexColour;

vec3 int_to_rgb(int integer)
{
	// python's colorsys.hsv_to_rgb function
	float hue = integer / 20480.0;
	float saturation = 0.5;
	float value = 0.0;
	
    int i = int(hue * 6.0);
    float f = (hue * 6.0) - i;
    float p = (1.0 - saturation);
    float q = (1.0 - saturation * f);
    float t = (1.0 - saturation * (1.0 - f));
    switch (i % 6) {
		case 0:
			return vec3(value, t, p);
		case 1:
			return vec3(q, value, p);
		case 2:
			return vec3(p, value, t);
		case 3:
			return vec3(p, q, value);
		case 4:
			return vec3(t, p, value);
		case 5:
			return vec3(value, p, q);
	}
}

void main()
{
    position = vertexPosition;
    //normal = vertexNormal;
    //albedoUV = vertexTexCoord;
	
	//fake_Kd = abs(normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3);
	/* Vertex Scrambling Check */
	vertexIndexColour = int_to_rgb(gl_VertexID);
	
	gl_Position = gl_ModelViewProjectionMatrix * vec4(position, 1);
}
