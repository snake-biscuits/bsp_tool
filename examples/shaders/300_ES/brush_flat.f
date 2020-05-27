#version 300 es
out mediump vec4 outColour;

in mediump vec3 position;
in mediump vec3 normal;
in mediump vec2 texUV;
in mediump vec2 lightUV;
in mediump vec3 reflectivityColour;

uniform sampler2D activeTexture; /* NOT AN ATLAS*/
uniform sampler2D activeLightmap;

void main()
{
	mediump vec4 Ka = vec4(0.75, 0.75, 0.75, 1);
	//mediump float normColour = normal.x / 3 + 1/3 * normal.y / 3 + 2/3 * normal.z / 3;
	mediump vec4 Kd = vec4(1, 1, 1, 1);
	mediump vec4 albedo = texture2D(activeTexture, texUV);
	mediump vec4 lightmap = texture2D(activeLightmap, lightUV);

	//outColour = (Ka + Kd) * albedo;
	//outColour = vec4(texUV.x, texUV.y, 1, 1);
	outColour = vec4(reflectivityColour, 1) * albedo;
}
