from OpenGL.GL import *
from OpenGL.GLU import *
import math
from utils import *
import numpy as np
import copy

class Camera:
    instance = None

    @staticmethod
    def set_instance(camera):
        Camera.instance = camera

    def __init__(self, cam_angle=45, asp_ratio=1, near=0.1, far=1000, eye=Point(0, 0, 0), yaw_angle=0, pitch_angle=0):
        self.cam_angle = cam_angle
        self.asp_ratio = asp_ratio
        self.near = near
        self.far = far
        self.eye = eye
        self.yaw_angle = yaw_angle
        self.pitch_angle = pitch_angle
        # TODO: temp value to create field. maybe unnecessary?
        self.view_matrix = np.array([[1.0, 0.0, 0.0, 0.0], [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 1.0, 0.0], [0.0, 0.0, 0.0, 1.0]], dtype='float32')
        # initialize view matrix once everything else is set
        self.update_view_matrix() 
        # set instance
        Camera.set_instance(self)

    # TODO: potentially revisit this and use a custom matrix management system
    #   would not rely on GL and GLU functionality
    #   may need this: https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluPerspective.xml
    def set_projection(self):
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluPerspective(self.cam_angle, self.asp_ratio, self.near, self.far)

    # TODO: potentially revisit this and use a custom matrix management system
    #   would not rely on GL and GLU functionality
    #   may need this: https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml
    def place_camera(self):
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

        # compute point to look at using yaw angle and pitch angle (no roll allowed)
        yaw_angle_rad = math.radians(self.yaw_angle)
        pitch_angle_rad = math.radians(self.pitch_angle)
        look_x = self.eye.x - math.sin(yaw_angle_rad) * math.cos(pitch_angle_rad)
        look_y = self.eye.y - math.sin(pitch_angle_rad)
        look_z = self.eye.z - math.cos(yaw_angle_rad) * math.cos(pitch_angle_rad)

        # TODO: fix issues with pitch around 90 degrees
        gluLookAt(self.eye.x, self.eye.y, self.eye.z, look_x, look_y, look_z, 0.0, 1.0, 0.0)

    def update_view_matrix(self):
        # compute point to look at using yaw angle and pitch angle (no roll allowed)
        yaw_angle_rad = math.radians(self.yaw_angle)
        pitch_angle_rad = math.radians(self.pitch_angle)
        look_x = self.eye.x - math.sin(yaw_angle_rad) * math.cos(pitch_angle_rad)
        look_y = self.eye.y - math.sin(pitch_angle_rad)
        look_z = self.eye.z - math.cos(yaw_angle_rad) * math.cos(pitch_angle_rad)
        
        # TODO: fix issues with pitch around 90 degrees (might still exist, untested?)
        # gluLookAt equivalent here (https://registry.khronos.org/OpenGL-Refpages/gl2.1/xhtml/gluLookAt.xml)

        # create center
        center = Point(look_x, look_y, look_z)

        # calc F
        f = Vector(p=center, q=self.eye)

        # create up (0, 1, 0)
        # up = Vector(p=Point(0, 1, 0))

        # normalize f and up
        f_norm = Vector(p=center, q=self.eye) # same as f
        f_norm.normalize()

        up_norm = Vector(p=Point(0, 1, 0)) # same as up
        up_norm.normalize()

        # take cross product of fnorm and upnorm to get s
        s = f_norm.cross(up_norm)

        # normalize s
        s_norm = f_norm.cross(up_norm) # same as s
        s_norm.normalize()

        # use snorm to find u
        u = s_norm.cross(f_norm)

        # create M
        m = np.array([
            [s.dx, s.dy, s.dz, 0.0],
            [u.dx, u.dy, u.dz, 0.0],
            [-f_norm.dx, -f_norm.dy, -f_norm.dz, 0.0],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')

        # mult view matrix by M
        self.view_matrix = m @ self.view_matrix

        # translate matrix by (-eyex, -eyey, -eyez)
        tm = np.array([
            [1.0, 0.0, 0.0, -self.eye.x],
            [0.0, 1.0, 0.0, -self.eye.y],
            [0.0, 0.0, 1.0, -self.eye.z],
            [0.0, 0.0, 0.0, 1.0]
        ], dtype='float32')
        self.view_matrix = tm @ self.view_matrix

    # note: sliding does not support vertical angle adjustments
    #   the movement is always assumed to be level with the ground
    #   (essentially up is always Vector(Point(0, 1, 0)) for the math)
    def slide(self, du, dv, dn):
        yaw_angle_rad = math.radians(self.yaw_angle)
        look_dx = math.sin(yaw_angle_rad)
        look_dz = math.cos(yaw_angle_rad)

        # find new u vector (rotated x-axis) using cross product of new n vector (rotated z-axis)
        #   and v vector (up vector / y-axis)
        n = Vector(Point(look_dx, 0.0, look_dz))
        v = Vector(Point(0.0, 1.0, 0.0))
        u = n.cross(v)
        u.normalize()

        self.eye.x += du * u.dx + dn * n.dx
        self.eye.y += dv
        self.eye.z += du * u.dz + dn * n.dz

    def rotate_yaw(self, angle):
        self.yaw_angle += angle
        self.yaw_angle %= 360

    # TODO: if updating up axis, can support 90 degree angles
    #   clamping the angle between -90 and 90
    def rotate_pitch(self, angle):
        target_angle = self.pitch_angle + angle
        self.pitch_angle = min(89, target_angle)
        self.pitch_angle = max(-89, target_angle)

    def __repr__(self):
        return f'Camera eye at {self.eye} with yaw of {self.yaw_angle} and pitch of {self.pitch_angle}'