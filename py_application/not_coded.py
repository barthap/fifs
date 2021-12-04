import asyncio
import websockets
import json
import signal
import sys
import pprint
from utils import find_my_ip
from matplotlib import pyplot as plt
import numpy as np
from filterpy.kalman import KalmanFilter
from filterpy.common import Q_discrete_white_noise

pp = pprint.PrettyPrinter(indent=2)


def update_line(hl, new_data):
    hist_points = 5
    xdata, ydata, zdata = hl._verts3d
    hl.set_xdata(np.array(np.append(xdata[-hist_points:], new_data[0])))
    hl.set_ydata(np.array(np.append(ydata[-hist_points:], new_data[1])))
    hl.set_3d_properties(np.array(np.append(zdata[-hist_points:], new_data[2])))


def signal_handler(sig, frame):
    print('\nStopping server...')
    sys.exit(0)


def print_xyz(measurement):
    return f"x: {measurement['x']:.3f}  y: {measurement['y']:.3f}  z: {measurement['z']:.3f}"


def calculate_orientation(acc, mgr, mag):
    orient = 0
    return orient


def print_sensor_data(raw_json_string, axa, axg, axm, axr, f):
    json_data = json.loads(raw_json_string)
    print("\n\n\n\n")
    gyroscope = json_data['gyroscope']
    accelerometer = json_data['accelerometer']
    magnetometer = json_data['magnetometer']
    magnetometer_uncalibrated = json_data['magnetometerUncallibrated']
    device_motion = json_data['deviceOrientationData']

    if gyroscope is not None:

        print(f"Gyroscope: {print_xyz(gyroscope)}")
    else:
        print(f"Gyroscope: disabled" + ' ' * 30)

    if accelerometer is not None:
        print(f"Accelerometer:  {print_xyz(accelerometer)}")
    else:
        print(f"Accelerometer: disabled" + ' ' * 30)

    if magnetometer is not None:
        print(f"Magnetometer:  {print_xyz(magnetometer)}")
    else:
        print(f"Magnetometer: disabled" + ' ' * 30)

    if magnetometer_uncalibrated is not None:
        print(f"Magnetometer (uncalibrated):  {print_xyz(magnetometer_uncalibrated)}")
    else:
        print(f"Magnetometer (uncalibrated): disabled" + ' ' * 0)

    # nie chce mi sie tego pretty-printowac
    print("Device motion (raw data):")

    # Here I implemented data visualization
    f.predict()
    f.update(np.array([[accelerometer['x'], accelerometer['y'], accelerometer['z']],
                       [gyroscope['x'], gyroscope['y'], gyroscope['z']],
                       [magnetometer['x'], magnetometer['y'], magnetometer['z']]]).reshape(9, 1))
    print(f.x)
    update_line(axa, (accelerometer['x'], accelerometer['y'], accelerometer['z']))
    update_line(axg, (gyroscope['x'], gyroscope['y'], gyroscope['z']))
    update_line(axm, (f.x[0], f.x[1], f.x[2]))
    update_line(axr, (device_motion['rotation']['alpha'], device_motion['rotation']['beta'],
                      device_motion['rotation']['gamma']))
    plt.pause(0.001)

    plt.show(block=False)
    # pp.pprint(device_motion)


async def handler(websocket, path):
    # for loop - receives sensor data until phone disconnects.
    print("A phone has connected")
    map = plt.figure()
    ax_map = map.add_subplot(221, projection='3d')
    ax_map.set_xlabel("X axis")
    ax_map.set_ylabel("Y axis")
    ax_map.set_zlabel("Z axis")
    ax_map.set_xlim3d([-2.0, 2.0])
    ax_map.set_ylim3d([-2.0, 2.0])
    ax_map.set_zlim3d([-2.0, 2.0])
    ax_map.grid(False)
    ax_map.set_title("Acceleration measured by phone's sensors")
    axa, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(222, projection='3d')
    ax_map.set_xlabel("X axis")
    ax_map.set_ylabel("Y axis")
    ax_map.set_zlabel("Z axis")
    ax_map.set_xlim3d([-5.0, 5.0])
    ax_map.set_ylim3d([-5.0, 5.0])
    ax_map.set_zlim3d([-5.0, 5.0])
    ax_map.grid(False)
    ax_map.set_title("Gyroscope measurement")
    axg, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(223, projection='3d')
    ax_map.set_xlabel("X axis")
    ax_map.set_ylabel("Y axis")
    ax_map.set_zlabel("Z axis")
    ax_map.set_xlim3d([-8.0, 8.0])
    ax_map.set_ylim3d([-8.0, 8.0])
    ax_map.set_zlim3d([-8.0, 8.0])
    ax_map.grid(False)
    ax_map.set_title("Magnotometr measurement")
    axm, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(224, projection='3d')
    ax_map.set_xlabel("Alpha")
    ax_map.set_ylabel("Beta")
    ax_map.set_zlabel("Gamma")
    ax_map.set_xlim3d([-8.0, 8.0])
    ax_map.set_ylim3d([-8.0, 8.0])
    ax_map.set_zlim3d([-8.0, 8.0])
    ax_map.grid(False)
    ax_map.set_title("Rotation measurement")
    axr, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    print("Plot was initialized")

    f = KalmanFilter(dim_x=3, dim_z=9)
    f.x = np.array([[0],
                    [0],
                    [0]])
    f.F = np.array([[1., 1., 1.],
                    [0., 1., 1.],
                    [0., 0., 1.]])
    f.H = np.array([[1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1],
                    [1, 1, 1]])
    f.P *= 1.
    f.R = np.eye(9) * 0.1
    f.Q = Q_discrete_white_noise(dim=3, dt=0.1, var=0.13)

    async for sensor_data in websocket:
        print_sensor_data(sensor_data, axa, axg, axm, axr, f)

    print("\nPhone disconnected.")


async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever


print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
signal.signal(signal.SIGINT, signal_handler)
asyncio.run(main())