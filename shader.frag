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
    vec3 scatteredLight = vec3(0.0);
    vec3 reflectedLight = vec3(0.0);

    // iterate over lights
    for (int light = 0; light < lights.length(); light++) {
        if (!lights[light].isEnabled)
            continue;
        
        vec3 halfVector;
        // TODO: this will not work properly
        vec3 lightDirection = lights[light].position;
        // vec3 lightDirection = vec3(1.0, 0.0, 0.0);
        float attenuation = 1.0;

        if (lights[light].isLocal) {
            lightDirection = lightDirection - vec3(fs_in.vertPosition);
            float lightDistance = length(lightDirection);
            lightDirection = lightDirection / lightDistance;

            attenuation = 1.0 / (lights[light].constantAttenuation + lights[light].linearAttenuation * lightDistance + lights[light].quadraticAttenuation * lightDistance * lightDistance);

            if (lights[light].isSpot) {
                float spotCos = dot(lightDirection, -lights[light].coneDirection);
                if (spotCos < lights[light].spotCosCutoff)
                    attenuation = 0.0;
                else
                    attenuation *= pow(spotCos, lights[light].spotExponent);
            }

            halfVector = normalize(lightDirection + eyeDirection);
        }
        else {
            lightDirection = lightDirection - vec3(fs_in.vertPosition);
            halfVector = lights[light].halfVector;
        }

        float diffuse = max(0.0, dot(fs_in.vertNormal, lightDirection));
        float specular = max(0.0, dot(fs_in.vertNormal, halfVector));

        if (diffuse == 0.0)
            specular = 0.0;
        else
            specular = pow(specular, materials[matIndex].shininess) * lights[light].specularStrength;

        scatteredLight += lights[light].ambient * materials[matIndex].ambient * attenuation + lights[light].color * materials[matIndex].diffuse * diffuse * attenuation;
        // reflectedLight += lights[light].color * materials[matIndex].specular * specular * attenuation;
    }

    vec3 rgb = min(materials[matIndex].emission + fs_in.vertColor.rgb * scatteredLight + reflectedLight, vec3(1.0));
    fragColor = vec4(rgb, fs_in.vertColor.a);

    // fragColor = fs_in.vertColor;
}