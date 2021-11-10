import { NavigationContainer } from "@react-navigation/native";
import { StatusBar } from "expo-status-bar";
import React from "react";
import SensorsScreen from "./SensorsScreen";
import { SafeAreaView } from "react-native-safe-area-context";
import { updateSensorData } from "./SensorData";
import ConnectionPanel from "./ConnectionPanel";

export default function App() {
  return (
    <NavigationContainer>
      <SafeAreaView style={{ flex: 1 }}>
        <StatusBar style="auto" />
        <ConnectionPanel />
        <SensorsScreen onData={updateSensorData} />
      </SafeAreaView>
    </NavigationContainer>
  );
}
