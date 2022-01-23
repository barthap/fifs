# FiFS

TODO

> Please don't touch the `mobile-app` and `.github` directories unless you know what you're doing ;)

## How it works

### Motion sensors

The cross-platform [Expo SDK](https://expo.dev) APIs are used to gather sensor data from a mobile device:

- [Gyroscope API](https://docs.expo.dev/versions/v43.0.0/sdk/gyroscope/)
- [Accelerometer API](https://docs.expo.dev/versions/v43.0.0/sdk/accelerometer/)
- [Magnetometer API](https://docs.expo.dev/versions/v43.0.0/sdk/magnetometer/) (both calibrated and uncalibrated)
- [Device Motion API](https://docs.expo.dev/versions/v43.0.0/sdk/devicemotion/) - A more high-level API which outputs the sensor data already processed - it can be used for comparison with _our sensoric fusion_ results. It outputs the following:

  - Acceleration (both with and without gravity)
  - Device orietnation (in radians)
  - Device rotation speed
  - Screen orientation (portrait/landscape/upside down)

  More info about the data can be found on the [API documentation page](https://docs.expo.dev/versions/v43.0.0/sdk/devicemotion/).

### To be continued

## How to run

### Running your app

1. These steps ensure that you have configured Python 3.x and `pip`. You can check your Python version by running:

   ```
   python --version

   # you could also try, it depends on your system
   python3 --version
   ```

1. Install the Python dependencies e.g. with `pip`:

   ```
   pip install -r requirements.txt
   ```

1. Install the **Expo Go** app ([Play Store link](https://play.google.com/store/apps/details?id=host.exp.exponent), [App Store link](https://apps.apple.com/pl/app/expo-go/id982107779)) on your phone. It is like a launcher for our app. It allows us to run the mobile app through a QR code on both Android and iOS, without publishing it to app/stores or downloading `.apk`.

1. Open terminal (command line prompt) and start the `run_app.py` script, with `-p` or `--platform` argument:

   ```
   # For android
   python3 run_app.py --platform android

   # For iOS
   python3 run_app.py --platform ios
   ```

1. The script outputs the QR code to your terminal. Scan it with your phone. On Android, there should be integrated barcode scanner in the _Expo Go_ app, for iOS you have to use the system Camera app.
   > If the QR code doesn't show up properly, search the terminal output for sth like `QR Code address: exp://192.168.0.101:8123/android-index.json`, copy that `exp://` address and paste it into an [online QR code generator](https://www.qr-code-generator.com/). Then scan it with your phone.
1. Don't close this terminal until you finish working with your app.
   > What the `run_app.py` does is to start HTTP server at port `8123` which the Expo Go uses to download our FiFS app code. It is similar to the OTA Updates mechanism.

### Running the WebSocket server for sensor data streaming

1. Do the steps from above. Have your app open and `run_app.py` running
1. In a separate console/terminal (don't close the previous one) run `server/base_template.py`, e.g.:
   ```
   cd server
   python main.py
   ```
1. When the script is started, it will show message like:
   ```
   WebSocket server listening at: ws://192.168.0.123:8765
   ```
1. Make sure that the IP in the mobile app is the same as the one displayed in the terminal. Change it if it's not
1. Click connect. Now the terminal should receive stream of messages like:
   ```
   Gyroscope: disabled
   Accelerometer: disabled
   Magnetometer: disabled
   Magnetometer (uncalibrated): disabled
   Device motion (raw data):
   None
   ```
1. Click the `Enable` buttons in the mobile app. Each sensor has its own button. The terminal on your computer should start receiving the sensor data. Example for Gyroscope and Accelerometer enabled:
   ```
   Gyroscope: x: -0.008  y: -0.006  z: 0.008
   Accelerometer: x: -0.080  y: -0.056  z: -0.989
   Magnetometer: disabled
   Magnetometer (uncalibrated): disabled
   Device motion (raw data):
   None
   ```
1. Open `server/base_template.py` in your favourite editor/IDE and take a look at the `print_sensor_data()` - it contains everything you need.
   > Currently, the mobile app is set up to send updates with 50ms interval, so this function is called 20 times a second.
1. Stop the previous script. Inside `server` directory, run `main.py` to Run the OpenGL application along with some plots.
   > NOTE: You need to click _Connect_ on the phone to get it working properly.
