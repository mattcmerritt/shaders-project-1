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
import copy
import pygame
from OpenGL.GL import *
import numpy as np
import math
from camera import *
from utils import *
from rendered_object import RenderedObject
from cube import Cube
from cylinder import Cylinder

camera_angle = 60.0
camera_start_position = Point(0.0, 0.0, 5.0)
window_dimensions = (640, 640)  # A tuple for the window dimensions
name = '3D Color Test'

# CONSTANTS FOR CUBES
# original color variant
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

old_colors = np.array([
    1.0, 0.0, 0.0, 1.0, # left, bottom, front
    0.0, 1.0, 0.0, 1.0, # left, bottom, back
    0.0, 0.0, 1.0, 1.0, # left, top, front
    1.0, 1.0, 1.0, 1.0, # left, top, back
    1.0, 1.0, 1.0, 1.0, # right, bottom, front
    0.0, 0.0, 1.0, 1.0, # right, bottom, back
    0.0, 1.0, 0.0, 1.0, # right, top, front
    1.0, 0.0, 0.0, 1.0, # right, top, back
], dtype='float32')

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

    # extra sanity checks
    version = glGetString(GL_VERSION).decode()
    print(f'OpenGL Version: {version}')

    # animation/object setup (preload values that will change here)
    global global_rotation
    global_rotation = 0

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
    glUseProgram(program) # NOTE: this line will fail if shaders do not compile
    
    # uniforms
    global proj_loc, modelview_loc

    proj_loc = glGetUniformLocation(program, "projectionMatrix")
    modelview_loc = glGetUniformLocation(program, "modelviewMatrix")

    # pass uniform locations to rendered object parent class
    RenderedObject.proj_loc = proj_loc
    RenderedObject.modelview_loc = modelview_loc

    # construct cubes
    global original_cube, new_cube
    original_cube = Cube(colors)
    new_cube = Cube(old_colors)

    # construct cylinder
    global cylinder
    cylinder = Cylinder(6, 2)

    # enable primitive restart 
    #   necessary for objects with multiple geometries in one VAO
    glEnable(GL_PRIMITIVE_RESTART)
    glPrimitiveRestartIndex(0xFFFF)

    # use depth test to only accept fragment if it is closer to the camera
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

# Callback function used to display the scene
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    # place camera
    # NOTE: placing the camera resets all matrices to identity
    camera.set_projection()
    camera.place_camera()

    # cube 1
    # glTranslatef(-3.0, 0.0, 0.0)
    # glRotatef(global_rotation, 0.0, 0.0, 1.0)
    # original_cube.draw_object()
    
    # cube 2
    # glRotatef(-global_rotation, 0.0, 0.0, 1.0)
    # glTranslatef(6.0, 0.0, 0.0)
    # glRotatef(global_rotation, 0.0, 0.0, 1.0)
    # new_cube.draw_object()

    # return to zero (not necessary)
    # glRotatef(-global_rotation, 0.0, 0.0, 1.0)
    # glTranslatef(-3.0, 0.0, 0.0)

    # cylinder
    # glTranslatef(0.0, -1.0, 0.0)
    # glScalef(1.0, 2.0, 1.0)
    # glRotatef(90.0, -1.0, 0.0, 0.0)
    cylinder.draw_object()

    glFlush()

# Advance the scene one frame
def advance():
    # rotate world by increasing angle
    global global_rotation
    global_rotation += 1.0
    global_rotation %= 360

# Function used to handle any key events
# event: The keyboard event that happened
def keyboard(event):
    global running, camera

    key = event.key # "ASCII" value of the key pressed
    if key == 27:  # ASCII code 27 = ESC-key
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
