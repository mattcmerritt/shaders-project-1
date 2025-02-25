import numpy as np
from OpenGL.GL import *
from rendered_object import RenderedObject

class Cube(RenderedObject):  
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

    indices = np.array([
        0, 1, 2, 3, 6, 7, 4, 5,     # first triangle strip
        0xFFFF,                     # start second triangle strip
        2, 6, 0, 4, 1, 5, 3, 7,     # second triangle strip
    ], dtype='uint16')

    def __init__(self, colors):
        # intialize vertex array object (VAO)
        self.vao = glGenVertexArrays(1)
        glBindVertexArray(self.vao)

        # initialize element array buffer (EBO)
        self.ebo = glGenBuffers(1)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ebo)
        glBufferData(GL_ELEMENT_ARRAY_BUFFER, len(Cube.indices) * 16, Cube.indices, GL_STATIC_DRAW)

        # initialize all VBOs
        # vertex buffer for positions
        # allocate a buffer object reference (will be an integer)
        self.vert_vbo = glGenBuffers(1)
        # specify the buffer to work with
        glBindBuffer(GL_ARRAY_BUFFER, self.vert_vbo)
        # populate the data of the buffer
        glBufferData(GL_ARRAY_BUFFER, len(Cube.vertices) * 32, Cube.vertices, GL_STATIC_DRAW)
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

        # TODO: remove debug
        # print(f'VAO {self.vao}, EBO {self.ebo}, pVBO {self.vert_vbo}, cVBO {self.color_vbo}')
        # bound_vao = glGetIntegerv(GL_VERTEX_ARRAY_BINDING)
        # bound_buffer = glGetIntegerv(GL_ARRAY_BUFFER_BINDING)
        # bound_element_buffer = glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING)
        # print(f'Currently bound VAO: {bound_vao}, current buffers: {bound_buffer}, current element buffer: {bound_element_buffer}')

        # unbind all objects
        # IMPORTANT: unbind VAO first to prevent detaching buffers
        glBindVertexArray(0)
        glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)
        glBindBuffer(GL_ARRAY_BUFFER, 0)

        # TODO: remove debug
        # bound_vao = glGetIntegerv(GL_VERTEX_ARRAY_BINDING)
        # bound_buffer = glGetIntegerv(GL_ARRAY_BUFFER_BINDING)
        # bound_element_buffer = glGetIntegerv(GL_ELEMENT_ARRAY_BUFFER_BINDING)
        # print(f'Currently bound VAO: {bound_vao}, current buffers: {bound_buffer}, current element buffer: {bound_element_buffer}')

    def draw_object(self): 
        # fetch most recent matrices for shaders
        RenderedObject.update_matrices()

        # rebind the vao
        glBindVertexArray(self.vao)

        # drawing vertices
        glDrawElements(GL_TRIANGLE_STRIP, len(Cube.indices), GL_UNSIGNED_SHORT, None)

        # unbind the vao
        glBindVertexArray(0)