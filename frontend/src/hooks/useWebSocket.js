import { useEffect, useRef } from "react";
import API_URL from "../api/config";
import { useAuth } from "../context/useAuth";

export default function useWebSocket(onMessageCallback) {
  const { accessToken } = useAuth();
  const callbackRef = useRef(onMessageCallback);

  useEffect(() => {
    callbackRef.current = onMessageCallback;
  }, [onMessageCallback]);

  useEffect(() => {
    if (!accessToken) return;
    // Detect correct protocol
    const wsProtocol = window.location.protocol === "https:" ? "wss" : "ws";
    const socketUrl = `${wsProtocol}://${API_URL.replace(
      /^https?:\/\//,
      ""
    )}/ws/stock-moves`;

    // WebSocket setup
    const socket = new WebSocket(socketUrl);

    socket.onopen = () => {
      socket.send(accessToken);  // Send the token immediately after connecting for authentication
    };

    socket.onmessage = (event) => {
      callbackRef.current(event.data);
    };

    return () => {
      socket.close();
    };
  }, [accessToken]);
}
