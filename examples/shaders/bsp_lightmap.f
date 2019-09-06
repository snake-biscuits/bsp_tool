#version 450 core
layout(location = 0) out vec4 outColour;

uniform sampler2D Texture0;

in vec2 lightUV;

void main()
{
    outColour = texture2D(Texture0, lightUV).rgba;
    outColour.rgb = outColour.rgb * pow(1.25, outColour.a);
}