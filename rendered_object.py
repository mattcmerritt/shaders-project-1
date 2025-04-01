import numpy as np
from OpenGL.GL import *
import math
from camera import *

class RenderedObject:
    proj_loc = None
    modelview_loc = None

    def __init__(self, model_matrix=np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype='float32')):
        self.model_matrix = model_matrix

    # this method allows for fetching the current transformation 
    #   matrices at the time an object is rendered.
    @staticmethod
    def update_matrices(modelview_matrix):
        # TODO: this should be handled in a parent class
        # access current transformation matrices

        # transformations go here
        # TODO: remove both? or use new ones instead
        proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
        # modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

        # print(f'proj: {proj_mat}')
        # print(f'mdvw: {modelview_mat}')

        # flatten the matrices to arrays
        flat_proj_mat = np.array(proj_mat).flatten()
        # flat_modelview_mat = np.array(modelview_mat).flatten()
        flat_modelview_mat = np.array(modelview_matrix).flatten()

        # load matrix values into uniforms for shader
        glUniformMatrix4fv(RenderedObject.proj_loc, 1, GL_FALSE, flat_proj_mat)
        glUniformMatrix4fv(RenderedObject.modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    def draw_object(self): 
        # TODO: make camera static
        # calc modelview matrix using model and view matrices
        # print(type(Camera.instance))
        modelview_matrix = Camera.instance.view_matrix @ self.model_matrix

        # fetch most recent matrices for shaders
        RenderedObject.update_matrices(modelview_matrix)

        # additional functionality will be handled by child classes
        pass

    def translate(self, x, y, z):
        translate_matrix = np.array([
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.model_matrix = translate_matrix @ self.model_matrix

    def scale(self, x, y, z):
        scale_matrix = np.array([
            [x, 0.0, 0.0, 0.0],
            [0.0, y, 0.0, 0.0],
            [0.0, 0.0, z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.model_matrix = scale_matrix @ self.model_matrix

    # TODO: can these three rotate functions be combined into one function? does the order matter?
    def rotate_around_x(self, deg):
        x_rot_matrix = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, math.cos(math.radians(deg)), -math.sin(math.radians(deg)), 0.0],
            [0.0, math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.model_matrix = x_rot_matrix @ self.model_matrix

    def rotate_around_y(self, deg):
        y_rot_matrix = np.array([
            [math.cos(math.radians(deg)), 0.0, math.sin(math.radians(deg)), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.model_matrix = y_rot_matrix @ self.model_matrix

    def rotate_around_z(self, deg):
        z_rot_matrix = np.array([
            [math.cos(math.radians(deg)), -math.sin(math.radians(deg)), 0.0, 0.0],
            [math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.model_matrix = z_rot_matrix @ self.model_matrix

    def apply_transform(self, transformation_matrix=np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype='float32')):
        self.model_matrix = transformation_matrix @ self.model_matrix