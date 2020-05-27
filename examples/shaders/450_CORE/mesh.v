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
out vec4 vertexIndexColour;

vec4 int_to_rgb(int integer)
{
	// based on python's colorsys module (hsv_to_rgb)
	float hue = integer / 65535;
	
	/*
	if s == 0.0:
        return v, v, v
    i = int(h*6.0) # XXX assume int() truncates!
    f = (h*6.0) - i
    p = v*(1.0 - s)
    q = v*(1.0 - s*f)
    t = v*(1.0 - s*(1.0-f))
    i = i%6
    if i == 0:
        return v, t, p
    if i == 1:
        return q, v, p
    if i == 2:
        return p, v, t
    if i == 3:
        return p, q, v
    if i == 4:
        return t, p, v
    if i == 5:
        return v, p, q
    # Cannot get here
	*/
	
	float R = ((integer >> 24) % 255) / 255.0;
	float G = ((integer >> 16) % 255) / 255.0;
	float B = ((integer >> 8) % 255) / 255.0;
	float A = (integer % 255) / 255.0;
	vec4 result = vec4(R, G, B, A);
	return result;
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
