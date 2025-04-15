import numpy as np
from OpenGL.GL import *
import math
from camera import *

class RenderedObject:
    proj_loc = None
    modelview_loc = None
    normal_proj_loc = None
    normal_modelview_loc = None

    def __init__(self, model_matrix=np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype='float32')):
        self.model_matrix = model_matrix

    # TODO: transpose all
    def translate(self, x, y, z):
        translate_matrix = np.array([
            [1.0, 0.0, 0.0, x],
            [0.0, 1.0, 0.0, y],
            [0.0, 0.0, 1.0, z],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        translate_matrix = np.transpose(translate_matrix)
        self.model_matrix = translate_matrix @ self.model_matrix

    def scale(self, x, y, z):
        scale_matrix = np.array([
            [x, 0.0, 0.0, 0.0],
            [0.0, y, 0.0, 0.0],
            [0.0, 0.0, z, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        scale_matrix = np.transpose(scale_matrix)
        self.model_matrix = scale_matrix @ self.model_matrix

    # TODO: can these three rotate functions be combined into one function? does the order matter?
    def rotate_around_x(self, deg):
        x_rot_matrix = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, math.cos(math.radians(deg)), -math.sin(math.radians(deg)), 0.0],
            [0.0, math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        x_rot_matrix = np.transpose(x_rot_matrix)
        self.model_matrix = x_rot_matrix @ self.model_matrix

    def rotate_around_y(self, deg):
        y_rot_matrix = np.array([
            [math.cos(math.radians(deg)), 0.0, math.sin(math.radians(deg)), 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-math.sin(math.radians(deg)), 0.0, math.cos(math.radians(deg)), 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        y_rot_matrix = np.transpose(y_rot_matrix)
        self.model_matrix = y_rot_matrix @ self.model_matrix

    def rotate_around_z(self, deg):
        z_rot_matrix = np.array([
            [math.cos(math.radians(deg)), -math.sin(math.radians(deg)), 0.0, 0.0],
            [math.sin(math.radians(deg)), math.cos(math.radians(deg)), 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        z_rot_matrix = np.transpose(z_rot_matrix)
        self.model_matrix = z_rot_matrix @ self.model_matrix

    def apply_transform(self, transformation_matrix=np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype='float32')):
        # transformation_matrix = np.transpose(transformation_matrix)
        self.model_matrix = transformation_matrix @ self.model_matrix

    # this method allows for fetching the current transformation 
    #   matrices at the time an object is rendered.
    @staticmethod
    def update_matrices(modelview_matrix):
        flat_proj_mat = np.array(Camera.instance.projection_matrix).flatten()
        flat_modelview_mat = np.array(modelview_matrix).flatten()

        # load matrix values into uniforms for shader
        glUniformMatrix4fv(RenderedObject.proj_loc, 1, GL_FALSE, flat_proj_mat)
        glUniformMatrix4fv(RenderedObject.modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    def draw_object(self): 
        modelview_matrix = self.model_matrix @ Camera.instance.view_matrix

        # fetch most recent matrices for shaders
        RenderedObject.update_matrices(modelview_matrix)

        # additional functionality will be handled by child classes
        pass

    # this method allows for fetching the current transformation 
    #   matrices at the time an object is rendered.
    # configured to work with a different program's uniform locations
    @staticmethod
    def update_normal_matrices(modelview_matrix):
        # # TODO: this should be handled in a parent class
        # # access current transformation matrices
        # proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
        # modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

        # # flatten the matrices to arrays
        # flat_proj_mat = np.array(proj_mat).flatten()
        # flat_modelview_mat = np.array(modelview_mat).flatten()

        flat_proj_mat = np.array(Camera.instance.projection_matrix).flatten()
        flat_modelview_mat = np.array(modelview_matrix).flatten()

        # load matrix values into uniforms for shader
        glUniformMatrix4fv(RenderedObject.normal_proj_loc, 1, GL_FALSE, flat_proj_mat)
        glUniformMatrix4fv(RenderedObject.normal_modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    def draw_normals(self):
        # fetch most recent matrices for shaders
        modelview_matrix = self.model_matrix @ Camera.instance.view_matrix
        RenderedObject.update_normal_matrices(modelview_matrix)

        # additional functionality will be handled by child classes
        # however, they should all call use GL_POINTS as the draw mode
        pass
