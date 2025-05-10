#version 460 core

// TODO: implement loading materials from vertices
// flat in int matIndex;
const int matIndex = 0;

in VS_OUT {
    vec4 vertPosition;
    vec4 vertColor;
    vec3 vertNormal;
} fs_in;

// TODO: make a class to build these on the OpenGL side
struct LightProperties {
    bool isEnabled;
    bool isLocal;
    bool isSpot;
    vec3 ambient;
    vec3 color;
    vec3 position;
    vec3 halfVector;
    vec3 coneDirection;
    float spotCosCutoff;
    float spotExponent;
    float constantAttenuation;
    float linearAttenuation;
    float quadraticAttenuation;
    float specularStrength;
};

// TODO: make a class to build these on the OpenGL side
struct MaterialProperties {
    vec3 emission;
    vec3 ambient;
    vec3 diffuse;
    vec3 specular;
    float shininess;
};

const int maxMaterials = 14;
uniform MaterialProperties materials[maxMaterials];

const int maxLights = 10;
uniform LightProperties lights[maxLights];
uniform vec3 eyeDirection;

uniform mat4 projectionMatrix;
uniform mat4 modelviewMatrix;

out vec4 fragColor;

void main() 
{
    vec3 lightDirection = lights[0].position;

    float diffuse = max(0.0, dot(fs_in.vertNormal, lightDirection));
    float specular = max(0.0, dot(fs_in.vertNormal, lights[0].halfVector));

    // vec3 scatteredLight = lights[0].ambient;
    vec3 scatteredLight = lights[0].ambient + lights[0].color * diffuse;
    vec3 fragRGB = min(fs_in.vertColor.rgb * scatteredLight, vec3(1.0));
    fragColor = vec4(fragRGB, fs_in.vertColor.a);
}