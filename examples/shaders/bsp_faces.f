#version 450 core
layout(location = 0) out vec4 outColour;

in vec3 position;
in smooth vec3 normal;
in vec2 texUV;
in vec2 lightUV;
in vec3 reflectivityColour;

uniform vec3 sun_vector;
uniform vec4 sun_colour;
uniform vec4 sun_ambient;

uniform sampler2D activeTexture; /* NOT AN ATLAS*/
uniform sampler2D activeLightmap;

void main()
{
	vec4 Ka = vec4(0.25, 0.25, 0.25, 1);
	vec4 sunlight = mix(sun_ambient, sun_colour, dot(normal, sun_vector));
	vec4 albedo = texture2D(activeTexture, texUV);
	vec4 lightmap = texture2D(activeLightmap, lightUV);

	// outColour = (Ka + Kd) * albedo;
	// outColour = vec4(texUV.x, texUV.y, 1, 1);
	// outColour = vec4(reflectivityColour, 1) * albedo;
	// outColour = vec4(reflectivityColour, 1) * albedo * (Ka + Kd);
	outColour = vec4(reflectivityColour, 1) * (sunlight + Ka);
}
