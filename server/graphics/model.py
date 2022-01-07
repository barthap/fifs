
import pywavefront

from OpenGL.GL import *
from OpenGL.GLU import *


class Model3D:
  def __init__(self, name):
    model = pywavefront.Wavefront(name, collect_faces=True, create_materials=True)

    scene_box = (model.vertices[0], model.vertices[0])
    for vertex in model.vertices:
        min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
        max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
        scene_box = (min_v, max_v)

    scene_size     = [scene_box[1][i]-scene_box[0][i] for i in range(3)]
    max_scene_size = max(scene_size)
    scaled_size    = 5

    self.__scene_scale    = [scaled_size/max_scene_size for i in range(3)]
    self.__scene_trans    = [-(scene_box[1][i]+scene_box[0][i])/2 for i in range(3)]
    self.model = model

  def draw(self):
        glEnable(GL_LIGHTING)
        glEnable(GL_LIGHT0)
        glEnable(GL_COLOR_MATERIAL)
        glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
        
        # rotate the model to match the phone's orientation
        glRotatef(180, 0, 0, 1)

        glPushMatrix()
        glScalef(*self.__scene_scale)
        glTranslatef(*self.__scene_trans)

        for mesh in self.model.mesh_list:
            glBegin(GL_TRIANGLES)
            for face in mesh.faces:
                for vertex_i in face:
                    glVertex3f(*self.model.vertices[vertex_i])
            glEnd()

        glPopMatrix()
        glDisable(GL_LIGHT0)
        glDisable(GL_LIGHTING)
        glDisable(GL_COLOR_MATERIAL)
  