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

uniform usampler2D Texture0;

void main()
{
    vec4 Ka = vec4(0.25, 0.25, 0.25, 1);
	vec4 sunlight = mix(sun_ambient, sun_colour, dot(normal, sun_vector));
    
    uvec4 rawLightmap = texture2D(Texture0, lightUV); // alpha holds exponent, ignore pls
    int exponent = int(rawLightmap.a);
    vec4 lightmap = vec4(0.1, 0.1, 0.1, 1) * pow(2, exponent);
    
    vec4 albedo = vec4(reflectivityColour, 1) * (lightmap + Ka);
    //float colour = exponent < 0.5 ? 1.0 : 0.0;
    //vec4 albedo = vec4(1, 1, 1, 1) * colour;
    
    outColour = albedo * sunlight;
    outColour = vec4(rawLightmap.r / 255, rawLightmap.g / 255, rawLightmap.b / 255, 1);
}