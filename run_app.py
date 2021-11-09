from http.server import HTTPServer, SimpleHTTPRequestHandler
from shutil import copyfile
import pyqrcode
import socket
from os.path import join
import signal
import sys


def signal_handler(sig, frame):
    print('\nStopping server...')
    sys.exit(0)


# nie pytajcie, skopiowane ze StackOverflow xD
def find_my_ip() -> str:
  ip =  (([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")] or [[(s.connect(("8.8.8.8", 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) + ["NO_IP_FOUND"])[0]
  if ip == "NO_IP_FOUND":
    raise Exception("Could not find your local IP address")
  return ip


def replace_file_contents(filename: str, old_string: str, new_string: str):
  # Safely read the input filename using 'with'
    with open(filename) as f:
        s = f.read()
        if old_string not in s:
            print('"{old_string}" not found in {filename}.'.format(**locals()))
            return

    # Safely write the changed content, if found in the file
    with open(filename, 'w') as f:
        print('Changing "{old_string}" to "{new_string}" in {filename}'.format(**locals()))
        s = s.replace(old_string, new_string)
        f.write(s)


my_ip = find_my_ip()
print(f"Detected IP address: {my_ip}")

DIRECTORY = join('.', 'mobile-app', 'dist')
class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

httpd = HTTPServer(('', 8123), Handler)

print("Generating app code for this computer")
ios_filename = join(DIRECTORY, 'ios-index.json')
android_filename = join(DIRECTORY, 'android-index.json')
# copy template files
copyfile(join(DIRECTORY, 'android-index.template.json'), android_filename)
copyfile(join(DIRECTORY, 'ios-index.template.json'), ios_filename)
# rename all occurrences of IP_TEMPLATE with actual IP addr in these files
replace_file_contents(ios_filename, 'IP_TEMPLATE', my_ip)
replace_file_contents(android_filename, 'IP_TEMPLATE', my_ip)

expo_addr = f"exp://{my_ip}:8123" 

qr = pyqrcode.create(expo_addr)
print(qr.terminal(quiet_zone=1))

print(f"Expo listening on {expo_addr}. Press Ctrl+C to exit.")
print("Install the 'Expo Go' app on your phone and scan the above QR code.")
signal.signal(signal.SIGINT, signal_handler)
httpd.serve_forever()
