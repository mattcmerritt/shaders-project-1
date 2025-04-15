from OpenGL.GL import *

class Light:
    # TODO: implement in a more strategic manner
    def __init__(self, index, program, is_enabled=True, is_local=False, is_spot=False, ambient=(0.0, 0.0, 0.0), color=(1.0, 1.0, 1.0), position=(0.0, 0.0, 0.0), half_vector=(0.0, 0.0, 0.0), cone_direction=(0.0, 0.0, 0.0), spot_cos_cutoff=0, spot_exponent=0, constant_attenuation=1, linear_attenuation=0, quadratic_attenuation=0, specular_strength=0):
        self.index = index
        self.program = program
        
        # load in the values, store in object memory
        self.is_enabled = is_enabled
        self.is_local = is_local
        self.is_spot = is_spot
        self.ambient = ambient
        self.color = color
        self.position = position
        self.half_vector = half_vector
        self.cone_direction = cone_direction
        self.spot_cos_cutoff = spot_cos_cutoff
        self.spot_exponent = spot_exponent
        self.constant_attenuation = constant_attenuation
        self.linear_attenuation = linear_attenuation
        self.quadratic_attenuation = quadratic_attenuation
        self.specular_strength = specular_strength

        # retrieve the uniform locations
        self.is_enabled_loc = glGetUniformLocation(self.program, f'lights[{index}].isEnabled')
        self.is_local_loc = glGetUniformLocation(self.program, f'lights[{index}].isLocal')
        self.is_spot_loc = glGetUniformLocation(self.program, f'lights[{index}].isSpot')
        self.ambient_loc = glGetUniformLocation(self.program, f'lights[{index}].ambient')
        self.color_loc = glGetUniformLocation(self.program, f'lights[{index}].color')
        self.position_loc = glGetUniformLocation(self.program, f'lights[{index}].position')
        self.half_vector_loc = glGetUniformLocation(self.program, f'lights[{index}].halfVector')
        self.cone_direction_loc = glGetUniformLocation(self.program, f'lights[{index}].coneDirection')
        self.spot_cos_cutoff_loc = glGetUniformLocation(self.program, f'lights[{index}].spotCosCutoff')
        self.spot_exponent_loc = glGetUniformLocation(self.program, f'lights[{index}].spotExponent')
        self.constant_attenuation_loc = glGetUniformLocation(self.program, f'lights[{index}].constantAttenuation')
        self.linear_attenuation_loc = glGetUniformLocation(self.program, f'lights[{index}].linearAttenuation')
        self.quadratic_attenuation_loc = glGetUniformLocation(self.program, f'lights[{index}].quadraticAttenuation')
        self.specular_strength_loc = glGetUniformLocation(self.program, f'lights[{index}].specularStrength')

        # assign initial values
        self.assign_uniform_values()

    def assign_uniform_values(self):
        glUniform1i(self.is_enabled_loc, 1 if self.is_enabled else 0)
        glUniform1i(self.is_local_loc, 1 if self.is_local else 0)
        glUniform1i(self.is_spot_loc, 1 if self.is_spot else 0)
        glUniform3f(self.ambient_loc, *self.ambient)
        glUniform3f(self.color_loc, *self.color)
        glUniform3f(self.position_loc, *self.position)
        glUniform3f(self.half_vector_loc, *self.half_vector)
        glUniform3f(self.cone_direction_loc, *self.cone_direction)
        glUniform1f(self.spot_cos_cutoff_loc, self.spot_cos_cutoff)
        glUniform1f(self.spot_exponent_loc, self.spot_exponent)
        glUniform1f(self.constant_attenuation_loc, self.constant_attenuation)
        glUniform1f(self.linear_attenuation_loc, self.linear_attenuation)
        glUniform1f(self.quadratic_attenuation_loc, self.quadratic_attenuation)
        glUniform1f(self.specular_strength_loc, self.specular_strength)