import pygame
from numpy import array
from math import cos, sin
import asyncio
import websockets
import bson
import signal
import sys
from utils import find_my_ip


BLACK, RED = (0, 0, 0), (255, 128, 128)

X, Y, Z = 0, 1, 2


def rotation_matrix(α, β, γ):
    """
    rotation matrix of α, β, γ radians around x, y, z axes (respectively)
    """
    sα, cα = sin(α), cos(α)
    sβ, cβ = sin(β), cos(β)
    sγ, cγ = sin(γ), cos(γ)
    return (
        (cβ*cγ, -cβ*sγ, sβ),
        (cα*sγ + sα*sβ*cγ, cα*cγ - sγ*sα*sβ, -cβ*sα),
        (sγ*sα - cα*sβ*cγ, cα*sγ*sβ + sα*cγ, cα*cβ)
    )


class Physical:
    def __init__(self, vertices, edges):
        """
        a 3D object that can rotate around the three axes
        :param vertices: a tuple of points (each has 3 coordinates)
        :param edges: a tuple of pairs (each pair is a set containing 2 vertices' indexes)
        """
        self.__vertices = array(vertices)
        self.__edges = tuple(edges)
        self.__rotation = [0, 0, 0]  # radians around each axis

    def rotate(self, axis, theta):
        self.__rotation[axis] += theta

    def set_rotation(self, axis, theta):
        self.__rotation[axis] = theta

    @property
    def lines(self):
        location = self.__vertices.dot(rotation_matrix(*self.__rotation))  # an index->location mapping
        return ((location[v1], location[v2]) for v1, v2 in self.__edges)


cube = Physical(  # 0         1            2            3           4            5            6            7
    vertices=((1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1), (-1, 1, 1), (-1, 1, -1), (-1, -1, 1), (-1, -1, -1)),
    edges=({0, 1}, {0, 2}, {2, 3}, {1, 3},
            {4, 5}, {4, 6}, {6, 7}, {5, 7},
            {0, 4}, {1, 5}, {2, 6}, {3, 7})
)

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


class Paint:
    def __init__(self, shape, loop):
        self.__shape = shape
        self.__size = 450, 450
        self.__screen = pygame.display.set_mode(self.__size)

    def __fit(self, vec):
        """
        ignore the z-element (creating a very cheap projection), and scale x, y to the coordinates of the screen
        """
        # notice that len(self.__size) is 2, hence zip(vec, self.__size) ignores the vector's last coordinate
        return [round(70 * coordinate + frame / 2) for coordinate, frame in zip(vec, self.__size)]

    def __draw_shape(self, thickness=4):
        for start, end in self.__shape.lines:
            pygame.draw.line(self.__screen, RED, self.__fit(start), self.__fit(end), thickness)

    def draw(self):
        self.__screen.fill(BLACK)
        self.__draw_shape()
        pygame.display.flip()
        # self.__clock.tick(40)

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
        ball.draw()

async def handle_events(event_queue):
    while True:
        event = await event_queue.get()
        if event.type == pygame.QUIT:
            break
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_SPACE:
        #         if ball.speed == [0, 0]:
        #             ball.speed = [2, 2]
        #         else:
        #             ball.speed = [0, 0]
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
