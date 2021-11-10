import Constants from "expo-constants";
import { SensorData } from "./SensorData";
import WebSocket from "isomorphic-ws";
import { URL } from "react-native-url-polyfill";

export const bestEffortWebsocketUrl = () => {
  const url = new URL(Constants.experienceUrl);
  url.port = "8765";
  url.pathname = "";
  return url.toString().replace("exp", "ws");
};

export class WebSocketManager {
  private _ws?: WebSocket;
  private connected: boolean = false;

  get isConnected() {
    return this.connected;
  }

  connect(url: string, onConnectChange?: (connected: boolean) => void) {
    this._ws = new WebSocket(bestEffortWebsocketUrl());

    this._ws.onopen = (e) => {
      console.log("WebSocket Connected");
      this.connected = true;
      onConnectChange?.(true);
    };

    this._ws.onmessage = (e) => {
      console.debug("Received:", e.data);
    };

    this._ws.onerror = (e) => {
      console.warn("WebSocket error:", e);
    };

    this._ws.onclose = (e) => {
      this.connected = false;
      console.log("WebSocket Disconnected:", e.code, e.reason);
      onConnectChange?.(false);
    };
  }

  disconnect() {
    console.debug("calling disconnect");
    this._ws?.close();
  }

  sendSensorData(data: SensorData) {
    if (this.isConnected) {
      this._ws?.send(JSON.stringify(data));
    }
  }
}
