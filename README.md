# FiFS

TODO

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

1. Install the **Expo Go** app ([Play Store link](), [App Store link]()) on your phone. It is like a launcher for our app. It allows us to run the mobile app through a QR code on both Android and iOS, without publishing it to app/stores or downloading `.apk`.

1. Open terminal and start the `run_app.py` script, with `-p` or `--platform` argument:

   ```
   # For android
   python3 run_app.py --platform android

   # For iOS
   python3 run_app.py --platform ios
   ```

1. The script outputs the QR code to your terminal. Scan it with your phone. On Android, there should be integrated barcode scanner in the _Expo Go_ app, for iOS you have to use the system Camera app.
1. Don't close this terminal until you finish working with your app.
   > What the `run_app.py` does is to start HTTP server at port `8123` which the Expo Go uses to download our FiFS app code. It is similar to the OTA Updates mechanism.
