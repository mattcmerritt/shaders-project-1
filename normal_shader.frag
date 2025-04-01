#version 460 core

in GS_OUT {
    vec4 vertPosition;
    vec4 vertColor;
    vec3 vertNormal;
} fs_in;

out vec4 fragColor;

void main() 
{
    fragColor = fs_in.vertColor;
}