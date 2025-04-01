#version 460 core

layout(location = 0) in vec4 position;
layout(location = 1) in vec4 color;
layout(location = 2) in vec3 normal;

uniform mat4 projectionMatrix;
uniform mat4 modelviewMatrix;

out vec4 vertColor;
out vec3 vertNormal;

void main() 
{
    gl_Position = projectionMatrix * (modelviewMatrix * position);
    vertColor = color;
    vertNormal = normal;
}