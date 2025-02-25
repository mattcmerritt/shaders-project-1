#==============================
# Matthew Merritt and Michael Merritt
# CSC699: GPU Programming and Rendering
#   Fall 2024
# Shader and GLSL Demo
#   Displays a simple rotating triangle with a primitive vertex and fragment shader
#   Demonstrates using uniform values to receive matrices and loading a VBO for
#   use in the shaders.
#==============================

import sys
import pygame
from OpenGL.GL import *
import numpy as np
import math
from camera import *
from utils import *

camera_angle = 60.0
window_dimensions = (640, 640)  # A tuple for the window dimensions
name = 'Hello World!'

def main():
    # Create the initial window
    init()
    
    # Listens for events and draws the scene
    main_loop()
    return

def main_loop():
    global running, clock
    while running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # (Re)draw the scene
        display()

        # Flipping causes the current image to be seen. (Double-Buffering)
        pygame.display.flip()

        clock.tick(60)  # limits FPS to 60

# Initialize some of the OpenGL matrices
def init():
    global clock, running
 
    # pygame setup
    pygame.init()
    screen = pygame.display.set_mode(window_dimensions, pygame.DOUBLEBUF|pygame.OPENGL)
    pygame.display.set_caption(name)
    clock = pygame.time.Clock()
    running = True

    # basic OpenGL setup
    # glMatrixMode(GL_PROJECTION)
    # glLoadIdentity()
    # glOrtho(0.0, 1.0, 0.0, 1.0, -1.0, 1.0)

    # camera configuration
    # TODO: find proper way to do this?
    camera = Camera(camera_angle, window_dimensions[0]/window_dimensions[1])
    camera.eye = Point(0.0, 0.0, 2.0)
    camera.set_projection()
    camera.place_camera()

    # configure shaders
    vertex_shader_source = ''
    with open('shader.vert', "r") as file:
        vertex_shader_source = file.readlines()

    fragment_shader_source = ''
    with open('shader.frag', "r") as file:
        fragment_shader_source = file.readlines()

    program = glCreateProgram()

    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)
    glAttachShader(program, vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)
    glAttachShader(program, fragment_shader)

    glLinkProgram(program)
    glUseProgram(program) # note: this line will fail if shaders do not compile
    
    # uniforms
    global proj_loc, modelview_loc

    proj_loc = glGetUniformLocation(program, "projectionMatrix")
    modelview_loc = glGetUniformLocation(program, "modelviewMatrix")

    # intialize vertex array object
    global vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # initialize vertex buffer
    # construct array for VBO, must be set to float32 for OpenGL
    vertices = np.array([
        0.5, 1, 0.0,
        math.sin(2 * math.pi / 3) / 2 + 0.5, math.cos(2 * math.pi / 3) / 2 + 0.5, 0.0,
        math.sin(-2 * math.pi / 3) / 2 + 0.5, math.cos(-2 * math.pi / 3) / 2 + 0.5, 0.0,
    ], dtype='float32')

    # allocate a buffer object reference (will be an integer)
    vert_vbo = glGenBuffers(1)
    # specify the buffer to work with
    glBindBuffer(GL_ARRAY_BUFFER, vert_vbo)
    # populate the data of the buffer
    glBufferData(GL_ARRAY_BUFFER, len(vertices) * 32, vertices, GL_STATIC_DRAW)
    # set the vertex pointer for the shader
    # note: 3 is the number of coordinates given in each vertex
    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
    # enable vertex array
    glEnableVertexAttribArray(0)

    # construct array for VBO, must be set to float32 for OpenGL
    colors = np.array([
        1.0, 0.0, 0.0, 1.0,
        0.0, 1.0, 0.0, 1.0,
        0.0, 0.0, 1.0, 1.0,
    ], dtype='float32')

    # allocate a buffer object reference (will be an integer)
    color_vbo = glGenBuffers(1)
    # specify the buffer to work with
    glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
    # populate the data of the buffer
    glBufferData(GL_ARRAY_BUFFER, len(colors) * 32, colors, GL_STATIC_DRAW)
    # set the vertex pointer for the shader
    # note: 3 is the number of coordinates given in each vertex
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
    # enable vertex array
    glEnableVertexAttribArray(1)

    # unbind vertex buffer and array objects
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

# Callback function used to display the scene
# Currently it just draws a simple polyline (LINE_STRIP)
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebind the vao
    glBindVertexArray(vao)

    # access current transformation matrices
    proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
    modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

    # flatten the matrices to arrays
    flat_proj_mat = np.array(proj_mat).flatten()
    flat_modelview_mat = np.array(modelview_mat).flatten()

    # load matrix values into uniforms for shader
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, flat_proj_mat)
    glUniformMatrix4fv(modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    # drawing vertices
    glDrawArrays(GL_TRIANGLE_FAN, 0, 3)

    # unbind the vao
    glBindVertexArray(vao)

    # perform rotation from center of screen
    #   rotation of 1 degree every frame
    glTranslatef(0.5, 0.5, 0.0)
    glRotatef(1.0, 0.0, 0.0, 1.0)
    glTranslatef(-0.5, -0.5, 0.0)

    glFlush()

if __name__ == '__main__': main()
