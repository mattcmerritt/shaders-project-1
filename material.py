from OpenGL.GL import *

class Material:
    # TODO: implement in a more strategic manner
    def __init__(self, index, program, emission=(0.0, 0.0, 0.0), ambient=(1.0, 1.0, 1.0), diffuse=(1.0, 1.0, 1.0), specular=(1.0, 1.0, 1.0), shininess=0):
        self.index = index
        self.program = program
        
        # load in the values, store in object memory
        self.emission = emission
        self.ambient = ambient
        self.diffuse = diffuse
        self.specular = specular
        self.shininess = shininess

        # retrieve the uniform locations
        self.emission_loc = glGetUniformLocation(self.program, f'materials[{index}].emission')
        self.ambient_loc = glGetUniformLocation(self.program, f'materials[{index}].ambient')
        self.diffuse_loc = glGetUniformLocation(self.program, f'materials[{index}].diffuse')
        self.specular_loc = glGetUniformLocation(self.program, f'materials[{index}].specular')
        self.shininess_loc = glGetUniformLocation(self.program, f'materials[{index}].shininess')

        # assign initial values
        self.assign_uniform_values()

    def assign_uniform_values(self):
        glUniform3f(self.emission_loc, *self.emission)
        glUniform3f(self.ambient_loc, *self.ambient)
        glUniform3f(self.diffuse_loc, *self.diffuse)
        glUniform3f(self.specular_loc, *self.specular)
        glUniform1f(self.shininess_loc, self.shininess)