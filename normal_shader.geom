#version 460 core

layout (points) in;
layout (line_strip, max_vertices = 2) out;

in VS_OUT {
    vec4 vertPosition;
    vec4 vertColor;
    vec3 vertNormal;
} gs_in[];

out GS_OUT {
    vec4 vertPosition;
    vec4 vertColor;
    vec3 vertNormal;
} gs_out;

void main()
{
    int n;

    for (n = 0; n < gs_in.length(); n++) {
        gl_Position = gs_in[n].vertPosition;
        gs_out.vertPosition = gl_Position;
        gs_out.vertColor = gs_in[n].vertColor;
        gs_out.vertNormal = gs_in[n].vertNormal;
        EmitVertex();

        // gl_Position = gs_in[n].vertPosition + vec4(gs_in[n].vertNormal, 0.0); // this does cause depth issues?
        // gl_Position = gs_in[n].vertPosition + vec4(0.0, 1.0, 0.0, 0.0); // this one does not cause depth issues
        gl_Position = gs_in[n].vertPosition + vec4(0.0, 0.0, -1.0, 0.0); // this one does not show anything?
        gl_Position = gs_in[n].vertPosition + vec4(gs_in[n].vertNormal.xy, 0.0, 0.0); // this works?
        gs_out.vertPosition = gl_Position;
        gs_out.vertColor = gs_in[n].vertColor;
        gs_out.vertNormal = gs_in[n].vertNormal;
        EmitVertex();
    }
    EndPrimitive();
}