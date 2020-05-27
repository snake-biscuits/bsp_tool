#version 450 core
layout(location = 0) out vec4 outColour;

/* Vertex Data */
in vec3 position;
// in smooth vec3 normal;
// in vec2 albedoUV;

//in float fake_Kd;

void main()
{
	vec4 Ka = vec4(0.25, 0.25, 0.25, 1); // Ka = ambient
	// vec3 light_colour = vec3(1, 1, 1);
	// float light_intensity = 10;
	// vec3 light_ray = vec3(1, 1, 1);
	// vec4 Kd = light_intensity * dot(normal, light_ray) * vec4(light_colour, 1); // Kd = diffuse
	vec4 Kd = vec4(1, 1, 1, 1);// * fake_Kd; // Kd = diffuse
	
	outColour = vec4(.5, .5, .5, 1) * (Ka + Kd);
}
