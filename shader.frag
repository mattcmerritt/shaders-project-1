#version 460 core

in vec4 vertColor;
in vec3 vertNormal;

out vec4 fragColor;

void main() 
{
    fragColor = vertColor;
}