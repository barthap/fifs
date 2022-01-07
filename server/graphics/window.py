
from graphics.object import SceneObject
import pygame
from pygame.constants import DOUBLEBUF, OPENGL

from OpenGL.GL import *
from OpenGL.GLU import *

class Window:
    def __init__(self, shape: SceneObject, title: str, size=(1280, 720)):
        self.__shape = shape
        self.size = size
        pygame.display.set_caption(title)
        pygame.display.set_mode(self.size, DOUBLEBUF|OPENGL)
        self.font = pygame.font.SysFont('arial', 24)

        gluPerspective(45, self.aspect_ratio, 0.1, 50.0)
        glTranslatef(0.0,0.0, -10)

        glLight(GL_LIGHT0, GL_POSITION,  (0, 0, 0, 1)) # point light from the left, top, front
        glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.1, 1))
        glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 0.8, 1))

        glEnable(GL_DEPTH_TEST)

    def drawText(self, x, y, text):                                                
        textSurface = self.font.render(text, True, (255, 255, 66, 255), (0, 0, 0, 0))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

    def draw(self):
        yaw, pitch, roll = self.__shape.rotation

        self.__shape.draw()

        self.drawText(10, 70, f"yaw: {yaw:.3f}")
        self.drawText(10, 40, f"pitch: {pitch:.3f}")
        self.drawText(10, 10, f"roll: {roll:.3f}")
        pygame.display.flip()

    @property
    def aspect_ratio(self):
        return self.size[0] / self.size[1]
