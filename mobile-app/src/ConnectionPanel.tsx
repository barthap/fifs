import React from "react";
import {
  StyleSheet,
  Text,
  View,
  TextInput,
  TouchableOpacity,
} from "react-native";
import { getSensorData } from "./SensorData";
import { bestEffortWebsocketUrl, WebSocketManager } from "./WebSocketManager";

// const WS_MESSAGE_INTERVAL = 500; // 500ms = 2Hz
const WS_MESSAGE_INTERVAL = 50; // 200ms = 5Hz

export default function ConnectionPanel() {
  const [url, setUrl] = React.useState(bestEffortWebsocketUrl());
  const [connected, setConnected] = React.useState(false);

  const ws = React.useRef(new WebSocketManager()).current;

  React.useEffect(() => {
    if (connected) {
      const interval = setInterval(() => {
        ws.sendSensorData(getSensorData());
      }, WS_MESSAGE_INTERVAL);
      return () => {
        clearInterval(interval);
      };
    } else {
      return undefined;
    }
  }, [connected]);

  const connect = () => {
    ws.connect(url, setConnected);
  };
  const disconnect = () => {
    ws.disconnect();
  };

  React.useEffect(() => {
    return () => {
      if (ws.isConnected) {
        console.debug("Component clear, disconnected");
        ws.disconnect();
      }
    };
  }, []);

  return (
    <View style={styles.panel}>
      <Text>WebSocket Address:</Text>
      <TextInput
        style={styles.input}
        defaultValue={bestEffortWebsocketUrl()}
        onChangeText={setUrl}
      />
      <View style={styles.buttonContainer}>
        <TouchableOpacity onPress={connect} style={styles.button}>
          <Text style={connected ? styles.disabled : styles.enabled}>
            Connect
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          onPress={disconnect}
          style={[styles.button, styles.buttonRight]}
        >
          <Text style={connected ? styles.enabled : styles.disabled}>
            Disconnect
          </Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  buttonContainer: {
    flexDirection: "row",
    alignItems: "stretch",
  },
  button: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#eee",
    padding: 10,
  },
  buttonRight: {
    borderLeftWidth: 1,
    borderColor: "#ccc",
  },
  input: {
    height: 40,
    margin: 12,
    borderWidth: 1,
    padding: 10,
  },
  panel: {
    marginTop: 15,
    paddingHorizontal: 10,
    paddingBottom: 5,
    borderBottomColor: "#bbb",
    borderBottomWidth: 1,
  },
  enabled: {
    color: "black",
  },
  disabled: {
    color: "#888",
  },
});
