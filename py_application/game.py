import math
import pygame
from numpy import array
from math import cos, sin
import asyncio
from pygame.constants import DOUBLEBUF, OPENGL
import websockets
import bson
import signal
import sys
from utils import find_my_ip
import pywavefront

from OpenGL.GL import *
from OpenGL.GLU import *

BLACK, RED = (0, 0, 0), (255, 128, 128)

X, Y, Z = 0, 1, 2


class Physical:
    def __init__(self):
        """
        a 3D object that can rotate around the three axes
        :param vertices: a tuple of points (each has 3 coordinates)
        :param edges: a tuple of pairs (each pair is a set containing 2 vertices' indexes)
        """
        self.__rotation = [0, 0, 0]  # radians around each axis

    def set_rotation(self, axis, theta):
        self.__rotation[axis] = theta

    @property
    def rotation(self):
        return self.__rotation


cube = Physical()


def signal_handler(sig, frame):
    print('\nExiting...')
    print('Stopping server...')
    asyncio.get_event_loop().stop()
    pygame.quit()
    sys.exit(0)


def process_sensor_data(raw_bson_string):
    bson_data = bson.loads(raw_bson_string)
    gyroscope = bson_data['gyroscope']
    accelerometer = bson_data['accelerometer']
    magnetometer = bson_data['magnetometer']
    magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']
    device_motion = bson_data['deviceOrientationData']

    if device_motion == None:
        return

    cube.set_rotation(Y, -device_motion['rotation']['alpha'])
    cube.set_rotation(X, device_motion['rotation']['beta'])
    cube.set_rotation(Z, -device_motion['rotation']['gamma'])


async def handler(websocket, path):
    # for loop - receives sensor data until phone disconnects.
    print("A phone has connected")
    async for sensor_data in websocket:
        process_sensor_data(sensor_data)

    print("\nPhone disconnected.")


async def main_ws():
    print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever


verticies = (
    (1, -1, -1),
    (1, 1, -1),
    (-1, 1, -1),
    (-1, -1, -1),
    (1, -1, 1),
    (1, 1, 1),
    (-1, -1, 1),
    (-1, 1, 1)
    )

edges = (
    (0,1),
    (0,3),
    (0,4),
    (2,1),
    (2,3),
    (2,7),
    (6,3),
    (6,4),
    (6,7),
    (5,1),
    (5,4),
    (5,7)
    )


def draw_cube():
    glBegin(GL_LINES)
    for edge in edges:
        for vertex in edge:
            glVertex3fv(verticies[vertex])
    glEnd()


model = pywavefront.Wavefront('i phone x.obj', collect_faces=True, create_materials=True)

scene_box = (model.vertices[0], model.vertices[0])
for vertex in model.vertices:
    min_v = [min(scene_box[0][i], vertex[i]) for i in range(3)]
    max_v = [max(scene_box[1][i], vertex[i]) for i in range(3)]
    scene_box = (min_v, max_v)

scene_size     = [scene_box[1][i]-scene_box[0][i] for i in range(3)]
max_scene_size = max(scene_size)
scaled_size    = 5
scene_scale    = [scaled_size/max_scene_size for i in range(3)]
scene_trans    = [-(scene_box[1][i]+scene_box[0][i])/2 for i in range(3)]

def draw_model():
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE )
    
    # rotate the model to match the phone's orientation
    glRotatef(180, 0, 0, 1)

    glPushMatrix()
    glScalef(*scene_scale)
    glTranslatef(*scene_trans)

    for mesh in model.mesh_list:
        glBegin(GL_TRIANGLES)
        for face in mesh.faces:
            for vertex_i in face:
                glVertex3f(*model.vertices[vertex_i])
        glEnd()

    glPopMatrix()
    glDisable(GL_LIGHT0)
    glDisable(GL_LIGHTING)
    glDisable(GL_COLOR_MATERIAL)

# convert radians to degrees float
def rad_to_deg(rad):
    return rad * 180 / math.pi

lightfv = ctypes.c_float * 4

light_x = 0
light_y = 0
light_z = 0

class Paint:
    def __init__(self, shape: Physical, loop):
        self.__shape = shape
        self.size = 1280, 720
        self.__screen = pygame.display.set_mode(self.size, DOUBLEBUF|OPENGL)
        self.font = pygame.font.SysFont('arial', 24)

    def drawText(self, x, y, text):                                                
        textSurface = self.font.render(text, True, (255, 255, 66, 255), (0, 0, 0, 0))
        textData = pygame.image.tostring(textSurface, "RGBA", True)
        glWindowPos2d(x, y)
        glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)
    def draw_cube_gl(self):
        r = self.__shape.rotation
        yaw = rad_to_deg(r[Y])
        pitch = rad_to_deg(r[X])
        roll = rad_to_deg(r[Z])

        glPushMatrix()

        # rotate the model to match the phone's orientation
        glRotatef(pitch, 1, 0, 0)
        glRotatef(-yaw, 0, 1, 0)
        glRotatef(roll, 0, 0, 1)

        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        # draw_cube()
        draw_model()
        glPopMatrix()

        self.drawText(10, 70, f"yaw: {yaw:.3f}")
        self.drawText(10, 40, f"pitch: {pitch:.3f}")
        self.drawText(10, 10, f"roll: {roll:.3f}")
        pygame.display.flip()


async def pygame_event_loop(event_queue):
    while True:
        await asyncio.sleep(0)
        event = pygame.event.poll()
        if event.type != pygame.NOEVENT:
            await event_queue.put(event)


async def draw(ball: Paint):
    black = 0, 0, 0

    current_time = 0
    while True:
        # last_time, current_time = current_time, time.time()
        # await asyncio.sleep(1 / 40 - (current_time - last_time))  # tick
        # ball.move()
        # screen.fill(black)
        # ball.draw(screen)
        # pygame.display.flip()
        await asyncio.sleep(40 / 1000)
        # ball.draw()
        ball.draw_cube_gl()


async def handle_events(event_queue):
    while True:
        event = await event_queue.get()
        if event.type == pygame.QUIT:
            break
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a:
                light_x += 1
            elif event.key == pygame.K_z:
                light_x -= 1
            elif event.key == pygame.K_s:
                light_y += 1
            elif event.key == pygame.K_x:
                light_y -= 1
            elif event.key == pygame.K_d:
                light_z += 1
            elif event.key == pygame.K_c:
                light_z -= 1

        # else:
        #     print("event", event)
    print("\nExiting event loop...")
    asyncio.get_event_loop().stop()
    print("Main loop stopped.")


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    loop = asyncio.get_event_loop()
    event_queue = asyncio.Queue()

    pygame.init()

    pygame.display.set_caption("Skalmar Game")

    ball = Paint(cube, loop)

    gluPerspective(45, ball.size[0]/ball.size[1], 0.1, 50.0)

    glTranslatef(0.0,0.0, -10)

    glLight(GL_LIGHT0, GL_POSITION,  (light_x, light_y, light_z, 1)) # point light from the left, top, front
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.1, 0.1, 0.1, 1))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1, 1, 0.8, 1))

    glEnable(GL_DEPTH_TEST)

    pygame_task = asyncio.ensure_future(pygame_event_loop(event_queue))
    event_task = asyncio.ensure_future(handle_events(event_queue))
    drawing_task = asyncio.ensure_future(draw(ball))
    websocket_task = asyncio.ensure_future(main_ws())

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        pygame_task.cancel()
        event_task.cancel()
        drawing_task.cancel()
        websocket_task.cancel()

    pygame.quit()
    print("Finishing")
