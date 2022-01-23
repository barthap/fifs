import time
import pygame
import asyncio
from pygame.constants import DOUBLEBUF, OPENGL
import websockets
import bson
import signal
import sys
from graphics.model import Model3D
from graphics.object import SceneObject
from graphics.window import Window
from kalman import Kalman
from plot import setup_plot, update_line
from utils import find_my_ip, rad_to_deg
import matplotlib.pyplot as plt
import numpy as np

from OpenGL.GL import *
from OpenGL.GLU import *

BLACK, RED = (0, 0, 0), (255, 128, 128)

X, Y, Z = 0, 1, 2



model = Model3D('models/iPhoneX.obj')
cube = SceneObject(model)

fusion = Kalman()


def signal_handler(sig, frame):
    print('\nExiting...')
    print('Stopping server...')
    asyncio.get_event_loop().stop()
    pygame.quit()
    sys.exit(0)


def process_sensor_data(raw_bson_string, axa, axg, axm, axr):
    bson_data = bson.loads(raw_bson_string)
    gyroscope = bson_data['gyroscope']
    accelerometer = bson_data['accelerometer']
    magnetometer = bson_data['magnetometer']
    magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']
    device_motion = bson_data['deviceOrientationData']
    

    if device_motion == None:
        return

    current_time = time.time()
    dt = current_time - process_sensor_data.last_time
    process_sensor_data.last_time = current_time

    fusion.computeAndUpdateRollPitchYaw(accelerometer['x'], accelerometer['y'], accelerometer['z'],
                                   gyroscope['x'], gyroscope['y'], gyroscope['z'],
                                   magnetometer['x'], magnetometer['y'], magnetometer['z'], dt,
                                   device_motion['rotation']['alpha'])

    alpha = device_motion['rotation']['alpha']
    beta = device_motion['rotation']['beta']
    gamma = device_motion['rotation']['gamma']
    alpha, beta, gamma = rad_to_deg(alpha), rad_to_deg(beta), rad_to_deg(gamma)
    cube.set_rotation(Y, -alpha)
    cube.set_rotation(X, beta)
    cube.set_rotation(Z, -gamma)
    # roll = 180 - fusion.roll if accelerometer['z'] > 0 else fusion.roll
    # cube.set_rotation(Y, -fusion.yaw)
    # cube.set_rotation(X, -fusion.pitch)
    # cube.set_rotation(Z, roll)

    update_line(axa, (accelerometer['x'], accelerometer['y'], accelerometer['z']))
    update_line(axg, (gyroscope['x'], gyroscope['y'], gyroscope['z']))
    update_line(axm, (magnetometer['x'], magnetometer['y'], magnetometer['z']))
    update_line(axr, (alpha, beta, gamma))
    plt.pause(0.001)

    plt.show(block=False)


process_sensor_data.last_time = time.time()


async def handler(websocket, path):
    # for loop - receives sensor data until phone disconnects.
    print("A phone has connected")
    _, axa, axg, axm, axr = setup_plot()
    async for sensor_data in websocket:
        process_sensor_data(sensor_data, axa, axg, axm, axr)

    print("\nPhone disconnected.")


async def main_ws():
    print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever


async def pygame_event_loop(event_queue):
    while True:
        await asyncio.sleep(0)
        event = pygame.event.poll()
        if event.type != pygame.NOEVENT:
            await event_queue.put(event)


async def draw(window: Window):
    current_time = 0
    while True:
        # last_time, current_time = current_time, time.time()
        # await asyncio.sleep(1 / 40 - (current_time - last_time))  # tick
        # ball.move()
        # screen.fill(BLACK)
        # ball.draw(screen)
        # pygame.display.flip()
        await asyncio.sleep(16 / 1000)
        window.draw()


async def handle_events(event_queue):
    while True:
        event = await event_queue.get()
        if event.type == pygame.QUIT:
            break
        # elif event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_ESCAPE:
        #         break
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

    window = Window(cube, title="Skalmar Game", size=(1280, 720))

    pygame_task = asyncio.ensure_future(pygame_event_loop(event_queue))
    event_task = asyncio.ensure_future(handle_events(event_queue))
    drawing_task = asyncio.ensure_future(draw(window))
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
