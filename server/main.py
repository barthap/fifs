import asyncio
import websockets
import bson
import signal
import sys
import pprint

from utils import find_my_ip

pp = pprint.PrettyPrinter(indent=2)

def signal_handler(sig, frame):
    print('\nStopping server...')
    sys.exit(0)


def print_xyz(measurement):
  return f"x: {measurement['x']:.3f}  y: {measurement['y']:.3f}  z: {measurement['z']:.3f}"

def print_sensor_data(raw_bson_string):
  bson_data = bson.loads(raw_bson_string)

  print("\n\n\n\n")

  gyroscope = bson_data['gyroscope']
  accelerometer = bson_data['accelerometer']
  magnetometer = bson_data['magnetometer']
  magnetometer_uncalibrated = bson_data['magnetometerUncallibrated']
  device_motion = bson_data['deviceOrientationData']

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
  pp.pprint(device_motion)


async def handler(websocket, path):
  # for loop - receives sensor data until phone disconnects.
  print("A phone has connected")
  async for sensor_data in websocket:
    print_sensor_data(sensor_data)
  
  print("\nPhone disconnected.")

async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever

print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
signal.signal(signal.SIGINT, signal_handler)
asyncio.run(main())
