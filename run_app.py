from http import HTTPStatus
from http.server import HTTPServer, SimpleHTTPRequestHandler
from shutil import copyfile
import pyqrcode
import json
from server.utils import find_my_ip
from os.path import join
import signal
import sys
import argparse

parser = argparse.ArgumentParser(description='Runs Expo dev server on specific platform.')
parser.add_argument('-p', '--platform', dest='platform',
                    help='Target platform. Valid values: android or ios',
                    choices=['android', 'ios'])
args = parser.parse_args()


def signal_handler(sig, frame):
    print('\nStopping server...')
    sys.exit(0)

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

  def do_POST(self):
    # the /logs endpoint handles console.log() from Expo app
    if self.path == '/logs':
      content_len = int(self.headers.get('Content-Length'))
      post_body = self.rfile.read(content_len).decode("utf-8") 
      logs = json.loads(post_body)
      for log in logs:
        body = " ".join(log['body'])
        print(f'[{log["level"]}] {body}')

      # self.send_response() logs the HTTP response info which spams the console.
      # These 3 lines send response without printing logs.
      self.send_response_only(HTTPStatus.OK, None)
      self.send_header('Server', self.version_string())
      self.send_header('Date', self.date_time_string())
    else:
      self.send_response(HTTPStatus.NOT_IMPLEMENTED)

httpd = HTTPServer(('', 8123), Handler)

print("\nGenerating app code for this computer")
ios_filename = join(DIRECTORY, 'ios-index.json')
android_filename = join(DIRECTORY, 'android-index.json')
# copy template files
copyfile(join(DIRECTORY, 'android-index.template.json'), android_filename)
copyfile(join(DIRECTORY, 'ios-index.template.json'), ios_filename)
# rename all occurrences of IP_TEMPLATE with actual IP addr in these files
replace_file_contents(ios_filename, 'IP_TEMPLATE', my_ip)
replace_file_contents(android_filename, 'IP_TEMPLATE', my_ip)

expo_addr = f"exp://{my_ip}:8123" 
platform = args.platform
if platform is None:
  print("\nSelect your phone platform. You can use the --platform cmd line arg to skip this prompt.")
  platform = input("Valid values are: 'android' and 'ios': ")

if platform != 'android' and platform != 'ios':
  raise Exception("Platform must be either android or ios! Quitting")

qr_addr = f"{expo_addr}/{platform}-index.json"
print(f"\nGenerated QR code for platform: {platform}")
print(f"QR Code address: {qr_addr}")
qr = pyqrcode.create(qr_addr, error='L')
print(qr.terminal(quiet_zone=1))

print(f"\nExpo listening on {expo_addr}. Press Ctrl+C to exit.")
print("Install the 'Expo Go' app on your phone and scan the above QR code.")
print("Your phone has to be in the same LAN network as this computer.")
signal.signal(signal.SIGINT, signal_handler)
httpd.serve_forever()
