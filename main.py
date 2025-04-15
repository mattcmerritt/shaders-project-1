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
from light import Light
from material import Material

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

single_color = np.array([
    1.0, 0.0, 1.0, 1.0, # left, bottom, front
    1.0, 0.0, 1.0, 1.0, # left, bottom, back
    1.0, 0.0, 1.0, 1.0, # left, top, front
    1.0, 0.0, 1.0, 1.0, # left, top, back
    1.0, 0.0, 1.0, 1.0, # right, bottom, front
    1.0, 0.0, 1.0, 1.0, # right, bottom, back
    1.0, 0.0, 1.0, 1.0, # right, top, front
    1.0, 0.0, 1.0, 1.0, # right, top, back
], dtype='float32')

def main():
    # Create the initial window
    init()

    # camera configuration
    global camera 
    camera = Camera(camera_angle, window_dimensions[0]/window_dimensions[1])
    camera.eye = copy.deepcopy(camera_start_position)
    # camera.eye = Point(0, 0, 0)
    camera.set_projection()
    # camera.place_camera()
    camera.update_view_matrix()
    
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
    with open('shader.vert', 'r') as file:
        vertex_shader_source = file.readlines()

    fragment_shader_source = ''
    with open('shader.frag', 'r') as file:
        fragment_shader_source = file.readlines()

    # main shader program
    global main_program
    main_program = glCreateProgram()

    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)
    glAttachShader(main_program, vertex_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)
    glAttachShader(main_program, fragment_shader)

    glLinkProgram(main_program)

    print(f'Main Program log: {glGetProgramInfoLog(main_program)}')
    print(f'Vertex Shader log: {glGetShaderInfoLog(vertex_shader)}')
    print(f'Fragment Shader log: {glGetShaderInfoLog(fragment_shader)}')

    glUseProgram(main_program) # NOTE: this line will fail if shaders do not compile

    # uniforms
    global proj_loc, modelview_loc

    proj_loc = glGetUniformLocation(main_program, 'projectionMatrix')
    modelview_loc = glGetUniformLocation(main_program, 'modelviewMatrix')

    # pass uniform locations to rendered object parent class
    RenderedObject.proj_loc = proj_loc
    RenderedObject.modelview_loc = modelview_loc

    # uniforms for lighting
    # light0_enabled = glGetUniformLocation(main_program, 'lights[0].isEnabled')
    # light0_ambient = glGetUniformLocation(main_program, 'lights[0].ambient')
    # light0_color = glGetUniformLocation(main_program, 'lights[0].color')
    # light0_position = glGetUniformLocation(main_program, 'lights[0].position')

    # glUniform1i(light0_enabled, 1)
    # glUniform3f(light0_ambient, 0.2, 0.2, 0.2)
    # glUniform3f(light0_color, 1.0, 1.0, 1.0)
    # glUniform3f(light0_position, 0.0, 3.0, 3.0)     # TODO: the light position will need to be transformed in shader

    # uniforms for lighting (handled by class)
    global light_0
    light_0 = Light(0, main_program, ambient=(0.2, 0.2, 0.2), position=(1.0, 0.0, 0.0))
    # TODO: add a place light function to move the light
    # light_1 = Light(1, main_program, color=(0.0, 0.0, 1.0), ambient=(0.2, 0.2, 0.2), position=(0.0, 0.0, 3.0))

    eyeDirection_loc = glGetUniformLocation(main_program, 'eyeDirection')
    glUniform3f(eyeDirection_loc, 0.0, 0.0, -1.0)

    # uniforms for materials
    # mat0_ambient = glGetUniformLocation(main_program, 'materials[0].ambient')
    # mat0_diffuse = glGetUniformLocation(main_program, 'materials[0].diffuse')
    # glUniform3f(mat0_ambient, 1.0, 1.0, 1.0)
    # glUniform3f(mat0_diffuse, 1.0, 1.0, 1.0)

    # uniforms for materials (handled by class)
    material_0 = Material(0, main_program, shininess=100)

    # adding secondary debug program for viewing normals
    # configure shaders
    vertex_shader_source = ''
    with open('normal_shader.vert', 'r') as file:
        vertex_shader_source = file.readlines()

    fragment_shader_source = ''
    with open('normal_shader.frag', 'r') as file:
        fragment_shader_source = file.readlines()

    geometry_shader_source = ''
    with open('normal_shader.geom', 'r') as file:
        geometry_shader_source = file.readlines()

    # secondary debug shader program
    global normal_view_program
    normal_view_program = glCreateProgram()

    vertex_shader = glCreateShader(GL_VERTEX_SHADER)
    glShaderSource(vertex_shader, vertex_shader_source)
    glCompileShader(vertex_shader)
    glAttachShader(normal_view_program, vertex_shader)

    geometry_shader = glCreateShader(GL_GEOMETRY_SHADER)
    glShaderSource(geometry_shader, geometry_shader_source)
    glCompileShader(geometry_shader)
    glAttachShader(normal_view_program, geometry_shader)

    fragment_shader = glCreateShader(GL_FRAGMENT_SHADER)
    glShaderSource(fragment_shader, fragment_shader_source)
    glCompileShader(fragment_shader)
    glAttachShader(normal_view_program, fragment_shader)

    glLinkProgram(normal_view_program)

    print(f'Normal Program log: {glGetProgramInfoLog(normal_view_program)}')
    print(f'Vertex Shader log: {glGetShaderInfoLog(vertex_shader)}')
    print(f'Geometry Shader log: {glGetShaderInfoLog(geometry_shader)}')
    print(f'Fragment Shader log: {glGetShaderInfoLog(fragment_shader)}')

    glUseProgram(normal_view_program) # NOTE: this line will fail if shaders do not compile

    # uniforms
    global normal_proj_loc, normal_modelview_loc

    normal_proj_loc = glGetUniformLocation(normal_view_program, 'projectionMatrix')
    normal_modelview_loc = glGetUniformLocation(normal_view_program, 'modelviewMatrix')

    # pass uniform locations to rendered object parent class
    RenderedObject.normal_proj_loc = normal_proj_loc
    RenderedObject.normal_modelview_loc = normal_modelview_loc

    # construct cubes
    global original_cube, new_cube, single_color_cube
    original_cube = Cube(colors)
    new_cube = Cube(old_colors)
    single_color_cube = Cube(single_color)

    # construct cylinder
    # global cylinder
    # cylinder = Cylinder(6, 2)

    # enable primitive restart 
    #   necessary for objects with multiple geometries in one VAO
    glEnable(GL_PRIMITIVE_RESTART)
    glPrimitiveRestartIndex(0xFFFF)

    # use depth test to only accept fragment if it is closer to the camera
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LESS)

    # set object transforms (model matrices)
    position_objects()

def position_objects():
    # TODO: determine why objects are moving away from one another
    new_cube.translate(3, 0, 0)

    original_cube.translate(0, 0, -3)
    original_cube.rotate_around_y(30)


# Callback function used to display the scene
def display():
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClear(GL_COLOR_BUFFER_BIT)
    glClear(GL_DEPTH_BUFFER_BIT)

    # place camera
    # NOTE: placing the camera resets all matrices to identity
    camera.set_projection()
    # camera.place_camera()
    camera.update_view_matrix()


    # LIGHT POSITION UPDATE
    # TODO: need to make lights have the same transformation abilities as rendered objects
    glUseProgram(main_program)
    world_pos = np.array([0.0, 5.0, 0.0, 1.0], dtype='float32')
    modelview_mat = np.array(glGetFloatv(GL_MODELVIEW_MATRIX), dtype='float32')
    light_0.position = (*(list(map(lambda x : x.item(), world_pos @ modelview_mat)))[:3],)
    # print(light_0.position)
    light_0.assign_uniform_values()

    # cube 1
    # glTranslatef(-3.0, 0.0, 0.0)
    # glRotatef(global_rotation, 0.0, 0.0, 1.0)
    original_cube.draw_object()

    # # transform cube (please work!)
    # original_cube.translate(1, 0, 0) # does same thing as holding a (left)

    # glRotatef(global_rotation, 0.0, 0.0, 1.0)
    # glRotatef(global_rotation, 0.0, 1.0, 0.0)
    single_color_cube.draw_object()
    glUseProgram(normal_view_program)
    single_color_cube.draw_normals()
    
    # cube 2
    # glRotatef(-global_rotation, 0.0, 0.0, 1.0)
    # glTranslatef(6.0, 0.0, 0.0)
    # glRotatef(global_rotation, 0.0, 0.0, 1.0)
    glUseProgram(main_program)
    new_cube.draw_object()

    # return to zero (not necessary)
    # glRotatef(-global_rotation, 0.0, 0.0, 1.0)
    # glTranslatef(-3.0, 0.0, 0.0)

    # cylinder
    # glTranslatef(0.0, -1.0, 0.0)
    # glScalef(1.0, 2.0, 1.0)
    # glRotatef(90.0, -1.0, 0.0, 0.0)
    # cylinder.draw_object()

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
        # camera.place_camera()
        camera.update_view_matrix()
    elif key == ord('t'):
        # Reset the camera angles
        camera.yaw_angle = 0
        camera.pitch_angle = 0
        # camera.place_camera()
        camera.update_view_matrix()
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
