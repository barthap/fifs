import math
import socket

# nie pytajcie, skopiowane ze StackOverflow xD
def find_my_ip() -> str:
  ip =  (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["NO_IP_FOUND"])[0]
  if ip == "NO_IP_FOUND":
    raise Exception("Could not find your local IP address")
  return ip


# convert radians to degrees float
def rad_to_deg(rad):
    return rad * 180 / math.pi
