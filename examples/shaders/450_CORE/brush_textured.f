#version 450 core
layout(location = 0) out vec4 outColour;

in vec3 position;
in smooth vec3 normal;
in vec2 texUV;
in vec2 lightUV;
in vec3 reflectivityColour;

uniform sampler2D activeTexture; /* NOT AN ATLAS*/
uniform sampler2D activeLightmap;

/*
uniform vec3 sun_vector;
uniform vec4 sun_colour;
uniform vec4 sun_ambient;
*/


void main()
{
	vec4 Ka = vec4(0.75, 0.75, 0.75, 1); // Ka = ambient
	vec4 Kd = vec4(1, 1, 1, 1) * normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3;
	vec4 albedo = texture2D(activeTexture, texUV);
	vec4 lightmap = texture2D(activeLightmap, lightUV);

	outColour = lightmap;
	// if (lightmap.a >= -.1) {
	// 	outColour = vec4(1, 0, 1, 0);
	// } else {
	// 	outColour = lightmap.a * vec4(1, 1, 1, 0) * 64;
	// }
	
	//outColour = (Ka + Kd) * albedo;
	//outColour = vec4(texUV.x, texUV.y, 1, 1);
	// outColour = vec4(reflectivityColour, 1) * (Ka + Kd) * albedo;
	// outColour = vec4(reflectivityColour, 1) * (Ka + Kd + sunlight) * albedo;
}
