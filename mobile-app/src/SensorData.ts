import * as Sensors from "expo-sensors";

export interface SensorData {
  gyroscope: Sensors.ThreeAxisMeasurement | null;
  accelerometer: Sensors.ThreeAxisMeasurement | null;
  magnetometer: Sensors.ThreeAxisMeasurement | null;
  magnetometerUncallibrated: Sensors.ThreeAxisMeasurement | null;
  deviceOrientationData: Sensors.DeviceMotionMeasurement | null;
}

const getInitialData: () => SensorData = () => ({
  gyroscope: null,
  accelerometer: null,
  magnetometer: null,
  magnetometerUncallibrated: null,
  deviceOrientationData: null,
});

let sensorData: SensorData = getInitialData();

export const getSensorData = () => sensorData;

export const updateSensorData = (newData: Partial<SensorData>) => {
  sensorData = { ...sensorData, ...newData };
};
