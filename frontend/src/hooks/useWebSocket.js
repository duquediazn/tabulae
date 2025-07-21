import { useEffect } from "react";
import API_URL from "../api/config";

export default function useWebSocket(onMessageCallback) {
  useEffect(() => {
    // Detect correct protocol
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${wsProtocol}://${API_URL.replace(
      /^https?:\/\//,
      ""
    )}/ws/stock-moves`;

    // WebSocket setup
    const socket = new WebSocket(socketUrl);

    socket.onmessage = (event) => {
      console.log("Message received:", event.data);
      onMessageCallback(event.data);
    };

    return () => {
      socket.close();
    };
  }, [onMessageCallback]);
}
