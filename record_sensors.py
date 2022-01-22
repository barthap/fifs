import asyncio
from cmath import nan
import websockets
import bson
import signal
import sys
import csv
from timeit import default_timer as timer

from server.utils import find_my_ip



file_handle = None


def signal_handler(sig, frame):
    print('\nStopping server...')
    if file_handle is not None:
      file_handle.close()
    sys.exit(0)


def print_sensor_data(raw_bson_string, writer, timestamp):
  bson_data = bson.loads(raw_bson_string)
  gyroscope = bson_data['gyroscope']
  accelerometer = bson_data['accelerometer']
  magnetometer = bson_data['magnetometer']
  magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']
  device_motion = bson_data['deviceOrientationData']

  row = [timestamp]
  
  if gyroscope is not None:
    row += [gyroscope['x'], gyroscope['y'], gyroscope['z']]
  else:
    row += [nan, nan, nan]

  if accelerometer is not None:
    row += [accelerometer['x'], accelerometer['y'], accelerometer['z']]
  else:
    row += [nan, nan, nan]

  if magnetometer is not None:
    row += [magnetometer['x'], magnetometer['y'], magnetometer['z']]
  else:
    row += [nan, nan, nan]

  if magnetometer_uncalibrated is not None:
    row += [magnetometer_uncalibrated['x'], magnetometer_uncalibrated['y'], magnetometer_uncalibrated['z']]
  else:
    row += [nan, nan, nan]

  if device_motion is not None:
    rotation = device_motion['rotation']
    row += [rotation['alpha'], rotation['beta'], rotation['gamma']]
  else:
    row += [nan, nan, nan]

  writer.writerow(row)
  

async def handler(websocket, path):
  # for loop - receives sensor data until phone disconnects.
  print("A phone has connected")
  global file_handle
  file_handle = open('sensors_data.csv', 'w')
  field_names = ['t',
    'acc_x', 'acc_y', 'acc_z',
    'gyro_x', 'gyro_y', 'gyro_z',
    'mag_x', 'mag_y', 'mag_z',
    'mag_x_uncalibrated', 'mag_y_uncalibrated', 'mag_z_uncalibrated',
    'rot_alpha', 'rot_beta', 'rot_gamma'
    ]
  writer = csv.writer(file_handle)
  writer.writerow(field_names)

  start = timer()
  async for sensor_data in websocket:
    time = timer() - start
    print_sensor_data(sensor_data, writer, time)

  
  file_handle.close()
  print("\nPhone disconnected.")


async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever

if __name__ == "__main__":
  print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
  signal.signal(signal.SIGINT, signal_handler)
  asyncio.run(main())
