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
import copy

camera_angle = 60.0
camera_start_position = Point(0.0, 0.0, 5.0)
window_dimensions = (640, 640)  # A tuple for the window dimensions
name = '3D Color Test'

# CONSTANTS FOR CUBES
# construct array for VBO, must be set to float32 for OpenGL
vertices = np.array([
    -1.0, -1.0, -1.0,   # left, bottom, front
    -1.0, -1.0, 1.0,    # left, bottom, back
    -1.0, 1.0, -1.0,    # left, top, front
    -1.0, 1.0, 1.0,     # left, top, back
    1.0, -1.0, -1.0,    # right, bottom, front
    1.0, -1.0, 1.0,     # right, bottom, back
    1.0, 1.0, -1.0,     # right, top, front
    1.0, 1.0, 1.0,      # right, top, back
], dtype='float32')

# construct array for VBO, must be set to float32 for OpenGL
colors = np.array([
    1.0, 0.0, 0.0, 1.0, # left, bottom, front
    0.0, 1.0, 0.0, 1.0, # left, bottom, back
    0.0, 0.0, 1.0, 1.0, # left, top, front
    1.0, 1.0, 1.0, 1.0, # left, top, back
    1.0, 1.0, 0.0, 1.0, # right, bottom, front
    0.0, 1.0, 1.0, 1.0, # right, bottom, back
    1.0, 0.0, 1.0, 1.0, # right, top, front
    0.2, 0.2, 0.2, 1.0, # right, top, back
], dtype='float32')

indices = np.array([
    0, 1, 2, 3, 6, 7, 4, 5,     # first triangle strip
    0xFFFF,                     # start second triangle strip
    2, 6, 0, 4, 1, 5, 3, 7,     # second triangle strip
], dtype='uint16')

def main():
    # Create the initial window
    init()

    # camera configuration
    global camera 
    camera = Camera(camera_angle, window_dimensions[0]/window_dimensions[1])
    camera.eye = copy.deepcopy(camera_start_position)
    camera.set_projection()
    camera.place_camera()
    
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
            elif event.type == pygame.KEYDOWN:
                keyboard(event)

        # advance frame (for animations, objects, other stuff being tracked)
        advance()

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
    # configures held inputs to repeat for the first time after 300ms, and then every 50ms afterwards
    #   action -> 300ms -> action -> 50ms -> action -> 50ms -> action ...
    pygame.key.set_repeat(300, 50)
    screen = pygame.display.set_mode(window_dimensions, pygame.DOUBLEBUF|pygame.OPENGL)
    pygame.display.set_caption(name)
    clock = pygame.time.Clock()
    running = True

    # animation/object setup (preload values that will change here)
    global tri_rotation
    tri_rotation = 0

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

    # intialize vertex array object (VAO)
    global vao
    vao = glGenVertexArrays(1)
    glBindVertexArray(vao)

    # initialize element array buffer (EBO)
    global ebo # TODO: this should not be necessary?
    ebo = glGenBuffers(1)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(indices) * 16, indices, GL_STATIC_DRAW)

    # initialize all VBOs
    # vertex buffer for positions
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

    # vertex buffer for colors
    # allocate a buffer object reference (will be an integer)
    color_vbo = glGenBuffers(1)
    # specify the buffer to work with
    glBindBuffer(GL_ARRAY_BUFFER, color_vbo)
    # populate the data of the buffer
    glBufferData(GL_ARRAY_BUFFER, len(colors) * 32, colors, GL_STATIC_DRAW)
    # set the vertex pointer for the shader
    # note: 4 is the number of coordinates given in each vertex
    glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
    # enable vertex array
    glEnableVertexAttribArray(1)

    # unbind all objects
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindVertexArray(0)

# Callback function used to display the scene
# Currently it just draws a simple polyline (LINE_STRIP)
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebind the vao
    glBindVertexArray(vao)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, ebo) # TODO: this should not be necessary?

    # enable primitive restart
    glEnable(GL_PRIMITIVE_RESTART)
    glPrimitiveRestartIndex(0xFFFF)

    # access current transformation matrices
    proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
    modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

    # flatten the matrices to arrays
    flat_proj_mat = np.array(proj_mat).flatten()
    flat_modelview_mat = np.array(modelview_mat).flatten()

    # load matrix values into uniforms for shader
    glUniformMatrix4fv(proj_loc, 1, GL_FALSE, flat_proj_mat)
    glUniformMatrix4fv(modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    # place camera
    camera.set_projection()
    camera.place_camera()

    # drawing vertices
    glDrawElements(GL_TRIANGLE_STRIP, len(indices), GL_UNSIGNED_SHORT, None)

    # unbind the vao
    glBindVertexArray(0)

    # perform rotation from center of screen
    #   rotation of 1 degree every frame
    glTranslatef(0.5, 0.5, 0.0)
    glRotatef(tri_rotation, 0.0, 0.0, 1.0)
    glTranslatef(-0.5, -0.5, 0.0)

    glFlush()

# Advance the scene one frame
def advance():
    # rotate triangle by increasing angle
    global tri_rotation
    tri_rotation += 1.0
    tri_rotation %= 360

# Function used to handle any key events
# event: The keyboard event that happened
def keyboard(event):
    global running, camera

    key = event.key # "ASCII" value of the key pressed
    if key == 27:  # ASCII code 27 = ESC-key
        # TODO: reimplement?
        running = False
    elif key == ord('r'):
        # Reset the camera position
        camera.eye = copy.deepcopy(camera_start_position)
        camera.place_camera()
    elif key == ord('t'):
        # Reset the camera angles
        camera.yaw_angle = 0
        camera.pitch_angle = 0
        camera.place_camera()
    elif key == ord('w'):
        # Go forward
        camera.slide(0,0,-1)
    elif key == ord('s'):
        # Go backward
        camera.slide(0,0,1)
    elif key == ord('a'):
        # Go left (relative to camera)
        camera.slide(1,0,0)
    elif key == ord('d'):
        # Go right (relative to camera)
        camera.slide(-1,0,0)
    elif key == ord('q'):
        # Turn camera left (counter-clockwise)
        camera.rotate_yaw(1)
    elif key == ord('e'):
        # Turn camera right (clockwise)
        camera.rotate_yaw(-1)
    elif key == ord('z'):
        # Rotate camera up
        camera.rotate_pitch(1)
    elif key == ord('x'):
        # Rotate camera down
        camera.rotate_pitch(-1)

if __name__ == '__main__': main()
