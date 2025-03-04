import numpy as np
import math
import random
from OpenGL.GL import *
from rendered_object import RenderedObject

class Cylinder(RenderedObject):
    # a cylinder is drawn from the base to the top, along the z-axis
    #   starting with the base's center at (0, 0, 0) and stopping with
    #   the base's center at (0, 0, 1).
    # slices is the number of points along the outer circle, and stacks
    #   is the number of layers drawn in the z-dimension
    def __init__(self, slices, stacks):
        # force stacks and slices to create a cylinder with volume at best
        stacks = max(stacks, 1)
        slices = max(slices, 3)

        # intialize vertex array object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # generate the vertices
        step_around = 2 * math.pi / slices
        step_out = 1 / stacks
        vertex_list = []
        for stack_index in range(stacks + 1):
            for slice_index in range(slices):
                theta = 2 * math.pi / slices * slice_index
                vertex_list.append(math.cos(theta))
                vertex_list.append(math.sin(theta))
                vertex_list.append(stack_index * step_out)

        # create numpy array with proper types for use with VBO
        vertices = np.array(vertex_list, dtype='float32')

        # generate the colors for each vertex
        #   currently, it will be a random color
        color_list = []
        for vertex_index in range(len(vertices) // 3):
            color_list.append(random.random())
            color_list.append(random.random())
            color_list.append(random.random())
            color_list.append(1.0)

        # create numpy array with proper types for use with VBO
        colors = np.array(color_list, dtype='float32')

        # generate the indices from the vertices determined earlier
        # begin by generating the outer faces that wrap around the cylinder
        main_indices = []
        # initially add the first point of the ring
        #   this must be done separately to prevent duplication with the last index in a stack
        #   and the first index in the nex stack overlapping.
        main_indices.append(0)
        for stack_index in range(stacks):
            # jump to the next ring over at the first slice (the 0th one)
            main_indices.append((stack_index + 1) * slices)
            # wrap around the rest of the outside, jumping between this ring and the next one
            for slice_index in range(1, slices):
                main_indices.append(slice_index + stack_index * slices)
                main_indices.append(slice_index + (stack_index + 1) * slices)
            # repeat the first point of both rings to close the shape
            main_indices.append(stack_index * slices)
            main_indices.append((stack_index + 1) * slices)

        # generate the indices for the end caps
        bottom_indices = []
        # start at the first slice
        bottom_indices.append(0)
        # adding some extra data for tracking where we are at in the triangulation
        remaining_points = slices - 1
        distance_from_start = 1
        on_opposite_side = False
        # triangulate the center by jumping between opposite sides of the start
        while remaining_points > 1:
            if not on_opposite_side:
                bottom_indices.append(distance_from_start)
                on_opposite_side = True
            else:
                bottom_indices.append(slices - distance_from_start)
                distance_from_start += 1
                on_opposite_side = False
            remaining_points -= 1
        # finish off the circle
        bottom_indices.append(math.ceil(slices / 2))

        top_indices = []
        # start at the first slice
        top_indices.append(stacks * slices)
        # adding some extra data for tracking where we are at in the triangulation
        remaining_points = slices - 1
        distance_from_start = 1
        on_opposite_side = False
        # triangulate the center by jumping between opposite sides of the start
        while remaining_points > 1:
            if not on_opposite_side:
                top_indices.append(stacks * slices + distance_from_start)
                on_opposite_side = True
            else:
                top_indices.append(stacks * slices + slices - distance_from_start)
                distance_from_start += 1
                on_opposite_side = False
            remaining_points -= 1
        # finish off the circle
        top_indices.append(stacks * slices + math.ceil(slices / 2))

        # create numpy array with proper types for use with EBO
        indices = np.array([
            *main_indices,
            0xFFFF,
            *bottom_indices,
            0xFFFF,
            *top_indices,
        ], dtype='uint16')
        self.num_indices = len(indices)

        # initialize element array buffer (EBO)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, self.num_indices * 16, indices, GL_STATIC_DRAW)

        # initialize all VBOs
        # vertex buffer for positions
        # allocate a buffer object reference (will be an integer)
        self.vert_vbo = glGenBuffers(1)
        # specify the buffer to work with
        glBindBuffer(GL_ARRAY_BUFFER, self.vert_vbo)
        # populate the data of the buffer
        glBufferData(GL_ARRAY_BUFFER, len(vertices) * 32, vertices, GL_STATIC_DRAW)
        # set the vertex pointer for the shader
        # note: 3 is the number of coordinates given in each vertex
        glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 0, None)
        # enable vertex array
        glEnableVertexAttribArray(0)

        # vertex buffer for colors
        # allocate a buffer object reference (will be an integer)
        self.color_vbo = glGenBuffers(1)
        # specify the buffer to work with
        glBindBuffer(GL_ARRAY_BUFFER, self.color_vbo)
        # populate the data of the buffer
        glBufferData(GL_ARRAY_BUFFER, len(colors) * 32, colors, GL_STATIC_DRAW)
        # set the vertex pointer for the shader
        # note: 4 is the number of coordinates given in each vertex
        glVertexAttribPointer(1, 4, GL_FLOAT, GL_FALSE, 0, None)
        # enable vertex array
        glEnableVertexAttribArray(1)

        # unbind all objects
        # IMPORTANT: unbind VAO first to prevent detaching buffers
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

    def draw_object(self): 
        super().draw_object()
        # rebind the vao
        glBindVertexArray(self.vao)
        # drawing vertices
        glDrawElements(GL_TRIANGLE_STRIP, self.num_indices, GL_UNSIGNED_SHORT, None)
        # unbind the vao
        glBindVertexArray(0)