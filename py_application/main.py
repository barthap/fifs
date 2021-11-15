import asyncio
import websockets
import json
import signal
import sys
import pprint
from utils import find_my_ip
from matplotlib import pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

pp = pprint.PrettyPrinter(indent=2)


def update_line(hl, new_data):
  hist_points = 15
  xdata, ydata, zdata = hl._verts3d
  hl.set_xdata(np.array(np.append(xdata[-hist_points:], new_data[0])))
  hl.set_ydata(np.array(np.append(ydata[-hist_points:], new_data[1])))
  hl.set_3d_properties(np.array(np.append(zdata[-hist_points:], new_data[2])))
  plt.pause(0.000001)
  plt.show(block=False)


def signal_handler(sig, frame):
    print('\nStopping server...')
    sys.exit(0)


def print_xyz(measurement):
  return f"x: {measurement['x']:.3f}  y: {measurement['y']:.3f}  z: {measurement['z']:.3f}"


def print_sensor_data(raw_json_string, axa, axg, axm, axr):
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
  update_line(axa, (accelerometer['x'], accelerometer['y'], accelerometer['z']))
  update_line(axg, (gyroscope['x'], gyroscope['y'], gyroscope['z']))
  update_line(axm, (magnetometer['x'], magnetometer['y'], magnetometer['z']))
  update_line(axr, (device_motion['rotation']['alpha'], device_motion['rotation']['beta'],
                    device_motion['rotation']['gamma']))
  pp.pprint(device_motion)


async def handler(websocket, path):
  # for loop - receives sensor data until phone disconnects.
  print("A phone has connected")
  map = plt.figure()
  ax_map = map.add_subplot(2, 2, 1, projection='3d')
  ax_map.set_xlabel("X axis")
  ax_map.set_ylabel("Y axis")
  ax_map.set_zlabel("Z axis")
  ax_map.set_xlim3d([-2.0, 2.0])
  ax_map.set_ylim3d([-2.0, 2.0])
  ax_map.set_zlim3d([-2.0, 2.0])
  ax_map.grid(False)
  ax_map.set_title("Acceleration measured by phone's sensors")
  axa, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
  ax_map = map.add_subplot(2, 2, 2, projection='3d')
  ax_map.set_xlabel("X axis")
  ax_map.set_ylabel("Y axis")
  ax_map.set_zlabel("Z axis")
  ax_map.set_xlim3d([-5.0, 5.0])
  ax_map.set_ylim3d([-5.0, 5.0])
  ax_map.set_zlim3d([-5.0, 5.0])
  ax_map.grid(False)
  ax_map.set_title("Gyroscope measurement")
  axg, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
  ax_map = map.add_subplot(2, 2, 3, projection='3d')
  ax_map.set_xlabel("X axis")
  ax_map.set_ylabel("Y axis")
  ax_map.set_zlabel("Z axis")
  ax_map.set_xlim3d([-50.0, 50.0])
  ax_map.set_ylim3d([-50.0, 50.0])
  ax_map.set_zlim3d([-50.0, 50.0])
  ax_map.grid(False)
  ax_map.set_title("Magnotometr measurement")
  axm, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')
  ax_map = map.add_subplot(2, 2, 4, projection='3d')
  ax_map.set_xlabel("Alpha")
  ax_map.set_ylabel("Beta")
  ax_map.set_zlabel("Gamma")
  ax_map.set_xlim3d([-360.0, 360.0])
  ax_map.set_ylim3d([-360.0, 360.0])
  ax_map.set_zlim3d([-360.0, 360.0])
  ax_map.grid(False)
  ax_map.set_title("Rotation measurement")
  axr, = ax_map.plot3D([0], [0], [0], marker='D', markersize=5, mec='y', mfc='r')

  async for sensor_data in websocket:
    print_sensor_data(sensor_data, axa, axg, axm, axr)
  
  print("\nPhone disconnected.")

async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever

print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
signal.signal(signal.SIGINT, signal_handler)
asyncio.run(main())
