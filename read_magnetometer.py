import asyncio
from cmath import nan
import websockets
import bson
import signal
import sys
import csv
import pprint

from server.utils import find_my_ip


pp = pprint.PrettyPrinter(indent=2)

file_handle = None


def signal_handler(sig, frame):
    print('\nStopping server...')
    if file_handle is not None:
      file_handle.close()
    sys.exit(0)


def print_sensor_data(raw_bson_string, writer):
  bson_data = bson.loads(raw_bson_string)
  magnetometer = bson_data['magnetometer']
  magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']


  row = []
  if magnetometer is not None:
    row += [magnetometer['x'], magnetometer['y'], magnetometer['z']]
  else:
    row += [nan, nan, nan]


  if magnetometer_uncalibrated is not None:
    row += [magnetometer_uncalibrated['x'], magnetometer_uncalibrated['y'], magnetometer_uncalibrated['z']]
  else:
    row += [nan, nan, nan]

  writer.writerow(row)
  

async def handler(websocket, path):
  # for loop - receives sensor data until phone disconnects.
  print("A phone has connected")
  global file_handle
  file_handle = open('magnetometer_data.csv', 'w')
  field_names = ['x', 'y', 'z', 'x_uncalibrated', 'y_uncalibrated', 'z_uncalibrated']
  writer = csv.writer(file_handle)
  writer.writerow(field_names)
  async for sensor_data in websocket:
    print_sensor_data(sensor_data, writer)
  
  file_handle.close()
  print("\nPhone disconnected.")


async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever


if __name__ == "__main__":
  print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
  signal.signal(signal.SIGINT, signal_handler)
  asyncio.run(main())
