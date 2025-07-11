import { buildGameWebsocketUrl } from "@/shared/utils";
import React, { createContext, useContext, useEffect, useRef, useState } from "react";

interface ProviderData {
  sendJSON: (message: any) => void;
  connected: boolean;
}

const WebSocketContext = createContext<ProviderData | undefined>(undefined);

interface ContextProps {
  gameUUID: string;
  onMessage?: (message: any) => void;
  children: React.ReactNode;
}

export const WebSocketContextProvider: React.FC<ContextProps> = ({ gameUUID, onMessage, children }) => {
  const websocketRef = useRef<WebSocket | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));
    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log("Websocket connected!");
      setConnected(true);
    };

    websocket.onmessage = (message) => {
      if (onMessage) {
        onMessage(message.data);
      }
    };

    websocket.onerror = () => {
      console.log("Websocket error");
      setConnected(false);
    };

    websocket.onclose = () => {
      console.log("Websocket closed");
      setConnected(false);
    };

    return () => {
      websocket.close();
    };
  }, []);

  const sendJSON = (message: object) => {
    if (!websocketRef.current) {
      console.error("Websocket is not open");
      return;
    }
    let encoded_message = JSON.stringify(message);
    websocketRef.current.send(encoded_message);
  };

  const contextValue: ProviderData = {
    connected: connected,
    sendJSON: sendJSON,
  };

  return <WebSocketContext.Provider value={contextValue}>{children}</WebSocketContext.Provider>;
};

export const useWebSocketContext = (): ProviderData => {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error("useWebSocketContext must be used within a WebSocketContextProvider");
  }
  return context;
};
