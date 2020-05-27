#version 300 es
in vec3 vertexPosition;
in vec3 vertexNormal;
in vec2 vertexTexCoord;
in vec2 vertexLightCoord;
in vec3 vertexColour;

uniform mat4 ProjectionMatrix;

out mediump vec3 position;
out mediump vec3 normal;
out mediump vec2 texUV;
out mediump vec2 lightUV;
out mediump vec3 reflectivityColour;

void main()
{
  position = vertexPosition;
  normal = vertexNormal;
  texUV = vec2(vertexTexCoord.x, -vertexTexCoord.y);
  lightUV = vertexLightCoord;
	reflectivityColour = vertexColour;

	gl_Position = ProjectionMatrix * vec4(vertexPosition, 1);
}
