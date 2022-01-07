# dupa
import asyncio
import websockets
import bson
import signal
import sys
import pprint
from utils import find_my_ip
from matplotlib import pyplot as plt
import numpy as np
import kalman
import time

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


def print_sensor_data(raw_bson_string, axa, axg, axm, axr, f: kalman.Kalman):
    bson_data = bson.loads(raw_bson_string)
    print("\n\n\n\n")
    gyroscope = bson_data['gyroscope']
    accelerometer = bson_data['accelerometer']
    magnetometer = bson_data['magnetometer']
    magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']
    device_motion = bson_data['deviceOrientationData']

    alpha = device_motion['rotation']['alpha']
    beta = device_motion['rotation']['beta']
    gamma = device_motion['rotation']['gamma']


    # if gyroscope is not None:

    #     print(f"Gyroscope: {print_xyz(gyroscope)}")
    # else:
    #     print(f"Gyroscope: disabled" + ' ' * 30)

    # if accelerometer is not None:
    #     print(f"Accelerometer:  {print_xyz(accelerometer)}")
    # else:
    #     print(f"Accelerometer: disabled" + ' ' * 30)

    # if magnetometer is not None:
    #     print(f"Magnetometer:  {print_xyz(magnetometer)}")
    # else:
    #     print(f"Magnetometer: disabled" + ' ' * 30)

    # if magnetometer_uncalibrated is not None:
    #     print(f"Magnetometer (uncalibrated):  {print_xyz(magnetometer_uncalibrated)}")
    # else:
    #     print(f"Magnetometer (uncalibrated): disabled" + ' ' * 0)

    # nie chce mi sie tego pretty-printowac

    print("Device motion (raw data):")
    print(f"alpha = {device_motion['rotation']['alpha']}, beta = {device_motion['rotation']['beta']},"
          f" gamma = {device_motion['rotation']['gamma']}")

    current_time = time.time()
    dt = current_time - print_sensor_data.last_time
    print_sensor_data.last_time = current_time

    print(f"dt = {dt}")

    # Here I implemented data visualization
    f.computeAndUpdateRollPitchYaw(accelerometer['x'], accelerometer['y'], accelerometer['z'],
                                   gyroscope['x'], gyroscope['y'], gyroscope['z'],
                                   magnetometer['x'], magnetometer['y'], magnetometer['z'], dt,
                                   device_motion['rotation']['alpha'])
    print("Device motion kalman:")
    print(f"alpha = {np.deg2rad(f.yaw)}, beta = {np.deg2rad(f.pitch)}, gamma = {np.deg2rad(f.roll)}")
    update_line(axa, (accelerometer['x'], accelerometer['y'], accelerometer['z']))
    update_line(axg, (gyroscope['x'], gyroscope['y'], gyroscope['z']))
    update_line(axm, (f.yaw, -f.pitch, -f.roll))
    update_line(axr, (np.rad2deg(alpha), np.rad2deg(beta), np.rad2deg(gamma)))
    plt.pause(0.001)

    plt.show(block=False)
    # pp.pprint(device_motion)
print_sensor_data.last_time = time.time()


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
    ax_map.set_xlabel("Alpha")
    ax_map.set_ylabel("Beta")
    ax_map.set_zlabel("Gamma")
    ax_map.set_xlim3d([-180, 180])
    ax_map.set_ylim3d([-180, 180])
    ax_map.set_zlim3d([-180, 180])
    ax_map.grid(True)
    ax_map.set_title("Rotation measurement Kalman")
    axm, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    ax_map = map.add_subplot(224, projection='3d')
    ax_map.set_xlabel("Alpha")
    ax_map.set_ylabel("Beta")
    ax_map.set_zlabel("Gamma")
    ax_map.set_xlim3d([-180, 180])
    ax_map.set_ylim3d([-180, 180])
    ax_map.set_zlim3d([-180, 180])
    ax_map.grid(True)
    ax_map.set_title("Rotation measurement")
    axr, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
    print("Plot was initialized")

    f = kalman.Kalman()
    a = 0
    async for sensor_data in websocket:
        if a == 0:
            print('initialization')
            bson_data = bson.loads(sensor_data)
            device_motion = bson_data['deviceOrientationData']
            f.yaw = device_motion['rotation']['alpha']
            f.pitch = device_motion['rotation']['beta']
            f.roll = device_motion['rotation']['gamma']
            a += 1
        print_sensor_data(sensor_data, axa, axg, axm, axr, f)

    print("\nPhone disconnected.")


async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever


print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
signal.signal(signal.SIGINT, signal_handler)
asyncio.run(main())
