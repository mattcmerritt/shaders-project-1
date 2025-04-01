import numpy as np
from OpenGL.GL import *

class RenderedObject:
    proj_loc = None
    modelview_loc = None

    normal_proj_loc = None
    normal_modelview_loc = None

    # this method allows for fetching the current transformation 
    #   matrices at the time an object is rendered.
    @staticmethod
    def update_matrices():
        # TODO: this should be handled in a parent class
        # access current transformation matrices
        proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
        modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

        # flatten the matrices to arrays
        flat_proj_mat = np.array(proj_mat).flatten()
        flat_modelview_mat = np.array(modelview_mat).flatten()

        # load matrix values into uniforms for shader
        glUniformMatrix4fv(RenderedObject.proj_loc, 1, GL_FALSE, flat_proj_mat)
        glUniformMatrix4fv(RenderedObject.modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    def draw_object(self): 
        # fetch most recent matrices for shaders
        RenderedObject.update_matrices()

        # additional functionality will be handled by child classes
        pass

    # this method allows for fetching the current transformation 
    #   matrices at the time an object is rendered.
    # configured to work with a different program's uniform locations
    @staticmethod
    def update_normal_matrices():
        # TODO: this should be handled in a parent class
        # access current transformation matrices
        proj_mat = glGetFloatv(GL_PROJECTION_MATRIX)
        modelview_mat = glGetFloatv(GL_MODELVIEW_MATRIX)

        # flatten the matrices to arrays
        flat_proj_mat = np.array(proj_mat).flatten()
        flat_modelview_mat = np.array(modelview_mat).flatten()

        # load matrix values into uniforms for shader
        glUniformMatrix4fv(RenderedObject.normal_proj_loc, 1, GL_FALSE, flat_proj_mat)
        glUniformMatrix4fv(RenderedObject.normal_modelview_loc, 1, GL_FALSE, flat_modelview_mat)

    def draw_normals(self):
        # fetch most recent matrices for shaders
        RenderedObject.update_normal_matrices()

        # additional functionality will be handled by child classes
        # however, they should all call use GL_POINTS as the draw mode
        pass