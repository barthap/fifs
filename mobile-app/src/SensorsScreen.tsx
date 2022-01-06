import { Subscription } from "expo-modules-core";
import * as Sensors from "expo-sensors";
import React from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TouchableOpacity,
  View,
} from "react-native";
import { SensorData } from "./SensorData";

const FAST_INTERVAL = 50; // 32ms = ~30Hz
const SLOW_INTERVAL = 1000; //ms

function Separator() {
  return (
    <View
      style={{
        marginTop: 15,
        borderBottomColor: "#bbb",
        borderBottomWidth: 1,
      }}
    />
  );
}

export default class SensorsScreen extends React.Component<{
  onData?: (data: Partial<SensorData>) => void;
}> {
  static navigationOptions = {
    title: "Sensors",
  };

  updateGyroscope = (data: any) => this.props.onData?.({ gyroscope: data });
  updateAccelerometer = (data: any) =>
    this.props.onData?.({ accelerometer: data });
  updateMagnetometer = (data: any) =>
    this.props.onData?.({ magnetometer: data });
  updateMagnetometerUncallibrated = (data: any) =>
    this.props.onData?.({ magnetometerUncallibrated: data });
  updateDeviceMotion = (data: any) =>
    this.props.onData?.({ deviceOrientationData: data });

  render() {
    return (
      <ScrollView style={styles.container}>
        <GyroscopeSensor onData={this.updateGyroscope} />
        <Separator />
        <AccelerometerSensor onData={this.updateAccelerometer} />
        <Separator />
        <MagnetometerSensor onData={this.updateMagnetometer} />
        <Separator />
        <MagnetometerUncalibratedSensor
          onData={this.updateMagnetometerUncallibrated}
        />
        <Separator />
        <DeviceMotionSensor onData={this.updateDeviceMotion} />
      </ScrollView>
    );
  }
}

interface State<M extends object> {
  data: M;
  isAvailable?: boolean;
  isEnabled?: boolean;
}

// eslint-disable-next-line @typescript-eslint/ban-types
abstract class SensorBlock<M extends object> extends React.Component<
  {
    onData?: (data: M | null) => void;
  },
  State<M>
> {
  readonly state: State<M> = { data: {} as M };

  _subscription?: Subscription;

  componentDidMount() {
    this.checkAvailability();
  }

  checkAvailability = async () => {
    const isAvailable = await this.getSensor().isAvailableAsync();
    this.setState({ isAvailable });
    if (!isAvailable) {
      this.props.onData?.(null);
    }
  };

  componentWillUnmount() {
    this._unsubscribe();
  }

  abstract getName: () => string;
  abstract getSensor: () => Sensors.DeviceSensor<M>;
  abstract renderData: () => JSX.Element;

  _toggle = () => {
    if (this._subscription) {
      this._unsubscribe();
    } else {
      this._subscribe();
    }
  };

  _slow = () => {
    this.getSensor().setUpdateInterval(SLOW_INTERVAL);
  };

  _fast = () => {
    this.getSensor().setUpdateInterval(FAST_INTERVAL);
  };

  _subscribe = () => {
    this._subscription = this.getSensor().addListener((data: any) => {
      this.setState({ data, isEnabled: true });
      this.props.onData?.(data);
    });
  };

  _unsubscribe = () => {
    this._subscription && this._subscription.remove();
    this._subscription = undefined;
    this.setState({ isEnabled: false });
    this.props.onData?.(null);
  };

  render() {
    if (this.state.isAvailable !== true) {
      return (
        <View style={styles.sensor}>
          <Text>{this.getName()}:</Text>
          <Text>This sensor is unavailable on this device</Text>
        </View>
      );
    }
    const toggleText = this.state.isEnabled ? "Disable" : "Enable";
    const textStyle = this.state.isEnabled ? styles.enabled : styles.disabled;
    return (
      <View style={styles.sensor}>
        <Text>{this.getName()}:</Text>
        {this.renderData()}
        <View style={styles.buttonContainer}>
          <TouchableOpacity onPress={this._toggle} style={styles.button}>
            <Text>{toggleText}</Text>
          </TouchableOpacity>
          <TouchableOpacity
            onPress={this._slow}
            style={[styles.button, styles.middleButton]}
          >
            <Text style={textStyle}>Slow</Text>
          </TouchableOpacity>
          <TouchableOpacity onPress={this._fast} style={styles.button}>
            <Text style={textStyle}>Fast</Text>
          </TouchableOpacity>
        </View>
      </View>
    );
  }
}

abstract class ThreeAxisSensorBlock extends SensorBlock<Sensors.ThreeAxisMeasurement> {
  renderData = () => (
    <Text style={this.state.isEnabled ? styles.enabled : styles.disabled}>
      x: {round(this.state.data.x)} y: {round(this.state.data.y)} z:{" "}
      {round(this.state.data.z)}
    </Text>
  );
}

class GyroscopeSensor extends ThreeAxisSensorBlock {
  getName = () => "Gyroscope";
  getSensor = () => Sensors.Gyroscope;
}

class AccelerometerSensor extends ThreeAxisSensorBlock {
  getName = () => "Accelerometer";
  getSensor = () => Sensors.Accelerometer;
}

class MagnetometerSensor extends ThreeAxisSensorBlock {
  getName = () => "Magnetometer";
  getSensor = () => Sensors.Magnetometer;
}

class MagnetometerUncalibratedSensor extends ThreeAxisSensorBlock {
  getName = () => "Magnetometer (Uncalibrated)";
  getSensor = () => Sensors.MagnetometerUncalibrated;
}

class DeviceMotionSensor extends SensorBlock<Sensors.DeviceMotionMeasurement> {
  getName = () => "DeviceMotion";
  getSensor = () => Sensors.DeviceMotion;
  renderXYZBlock = (
    name: string,
    event: null | { x?: number; y?: number; z?: number } = {}
  ) => {
    if (!event) return null;
    const { x, y, z } = event;
    return (
      <Text style={this.state.isEnabled ? styles.enabled : styles.disabled}>
        {name}: x: {round(x)} y: {round(y)} z: {round(z)}
      </Text>
    );
  };
  renderABGBlock = (
    name: string,
    event: null | { alpha?: number; beta?: number; gamma?: number } = {}
  ) => {
    if (!event) return null;

    const { alpha, beta, gamma } = event;
    return (
      <Text style={this.state.isEnabled ? styles.enabled : styles.disabled}>
        {name}: α: {round(alpha)} β: {round(beta)} γ: {round(gamma)}
      </Text>
    );
  };
  renderData = () => (
    <View>
      {this.renderXYZBlock("Acceleration", this.state.data.acceleration)}
      {this.renderXYZBlock(
        "Acceleration w/ gravity",
        this.state.data.accelerationIncludingGravity
      )}
      {this.renderABGBlock("Rotation", this.state.data.rotation)}
      {this.renderABGBlock("Rotation rate", this.state.data.rotationRate)}
      <Text style={this.state.isEnabled ? styles.enabled : styles.disabled}>
        Orientation: {this.state.data.orientation}
      </Text>
    </View>
  );
}

function round(n?: number) {
  if (!n) {
    return 0;
  }

  return Math.floor(n * 100) / 100;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    marginBottom: 10,
  },
  buttonContainer: {
    flexDirection: "row",
    alignItems: "stretch",
    marginTop: 15,
  },
  button: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#eee",
    padding: 10,
  },
  middleButton: {
    borderLeftWidth: 1,
    borderRightWidth: 1,
    borderColor: "#ccc",
  },
  sensor: {
    marginTop: 15,
    paddingHorizontal: 10,
  },
  enabled: {
    color: "black",
  },
  disabled: {
    color: "#888",
  },
});
