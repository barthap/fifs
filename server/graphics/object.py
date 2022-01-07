
from graphics.model import Model3D
from utils import rad_to_deg

from OpenGL.GL import *
from OpenGL.GLU import *

X, Y, Z = 0, 1, 2

class SceneObject:
    def __init__(self, model: Model3D):
        self.__model = model
        self.__rotation = [0, 0, 0]  # radians around each axis

    def set_rotation(self, axis, theta):
        self.__rotation[axis] = theta

    @property
    def rotation(self):
        r = self.__rotation
        yaw = r[Y]
        pitch = r[X]
        roll = r[Z]
        return yaw, pitch, roll

    def draw(self):
        yaw, pitch, roll = self.rotation

        glPushMatrix()

        # rotate the model to match the phone's orientation
        glRotatef(pitch, 1, 0, 0)
        glRotatef(-yaw, 0, 1, 0)
        glRotatef(roll, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # draw_cube()
        self.__model.draw()
        glPopMatrix()

