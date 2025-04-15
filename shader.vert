#version 460 core

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;

uniform mat4 projectionMatrix;
uniform mat4 modelviewMatrix;

out VS_OUT {
    vec4 vertPosition;
    vec4 vertColor;
    vec3 vertNormal;
} vs_out;

void main() 
{
    gl_Position = projectionMatrix * (modelviewMatrix * position);
    vs_out.vertPosition = modelviewMatrix * position;
    vs_out.vertColor = color;

    mat3 normalMatrix = mat3(transpose(inverse(modelviewMatrix)));
    vs_out.vertNormal = normalize(normalMatrix * normal);
}