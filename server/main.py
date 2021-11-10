import asyncio
import websockets

from utils import find_my_ip

async def handler(websocket, path):
  # for loop - receives sensor data until phone disconnects.
  print("A phone has connected")
  async for sensor_data in websocket:
    print(f"<<< {sensor_data}")
  
  print("Phone disconnected.")

async def main():
    async with websockets.serve(handler, port=8765):
        await asyncio.Future()  # run forever

print(f"WebSocket server listening at: ws://{find_my_ip()}:8765")
asyncio.run(main())
