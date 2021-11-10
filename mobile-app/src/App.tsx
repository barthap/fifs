import { NavigationContainer } from "@react-navigation/native";
import { StatusBar } from "expo-status-bar";
import React from "react";
import { StyleSheet, Text, View } from "react-native";
import SensorsScreen from "./SensorsScreen";
import { SafeAreaView } from "react-native-safe-area-context";
import Constants from "expo-constants";
import { URL } from "react-native-url-polyfill";

const bestEffortWebsocketUrl = () => {
  const url = new URL(Constants.experienceUrl);
  const { protocol, hostname, port, host, pathname, search, searchParams } =
    url;
  console.log(protocol, hostname, port, host, pathname, search, searchParams);
  url.port = "8765";
  url.pathname = "";
  return url.toString().replace("exp", "ws");
};

function HelloScreen() {
  return (
    <View style={styles.container}>
      <Text>TODO: Add expo-sensors code and WebSocket/Socket.IO</Text>
    </View>
  );
}

export default function App() {
  return (
    <NavigationContainer>
      <SafeAreaView style={{ flex: 1 }}>
        <StatusBar style="auto" />
        <Text>{bestEffortWebsocketUrl()}</Text>
        <SensorsScreen />
      </SafeAreaView>
    </NavigationContainer>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: "#fff",
    alignItems: "center",
    justifyContent: "center",
  },
});
