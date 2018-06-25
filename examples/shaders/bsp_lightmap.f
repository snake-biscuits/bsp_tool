#version 450 core
layout(location = 0) out vec4 outColour;

uniform sampler2D Texture0;

in vec2 uv;

void main()
{
    outColour = texture2D(Texture0, uv).rgba;
    outColour.rgb = outColour.rgb * pow(2, outColour.a);
}