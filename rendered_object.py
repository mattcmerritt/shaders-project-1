import numpy as np
from OpenGL.GL import *

class RenderedObject:
    proj_loc = None
    modelview_loc = None

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