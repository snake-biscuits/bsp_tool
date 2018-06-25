#version 450 core
layout(location = 0) out vec4 outColour;

in vec3 position;
in smooth vec3 normal;
in vec2 texUV;
in vec2 lightUV;
in vec3 reflectivityColour;

uniform sampler2D activeTexture; /* NOT AN ATLAS*/
uniform sampler2D activeLightmap;

void main()
{
	vec4 Ka = vec4(0.75, 0.75, 0.75, 1);
	vec4 Kd = vec4(1, 1, 1, 1) * normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3;
	vec4 albedo = texture2D(activeTexture, texUV);
	vec4 lightmap = texture2D(activeLightmap, lightUV);

	//outColour = (Ka + Kd) * albedo;
	//outColour = vec4(texUV.x, texUV.y, 1, 1);
	outColour = vec4(reflectivityColour, 1) * albedo;
}
