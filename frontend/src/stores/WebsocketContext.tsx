import { useReactQuerySubscription } from "@/hooks";
import React, { createContext, useEffect } from "react";
import { useWebsocketStore } from "./WebsocketStore";
import { WEBSOCKET_RECONNECT_DELAY } from "@/config";

interface WebsocketContextType {}

const WebsocketContext = createContext<WebsocketContextType | undefined>(undefined);

interface WebsocketContextProviderProps {
  mountWebsocket?: boolean;
}

function WebsocketService({ gameUUID }: { gameUUID: string }) {
  useReactQuerySubscription(gameUUID);
  return null;
}

export const WebsocketContextProvider: React.FC<WebsocketContextProviderProps> = () => {
  const value: WebsocketContextType = {};
  const gameUUID = window.location.pathname.split("/")[2];
  const [mountWebsocket, setMountWebsocket] = React.useState(true);
  const { connected } = useWebsocketStore();

  useEffect(() => {
    console.log("websocketConnected", connected);
    let interval: NodeJS.Timeout | undefined;

    if (!connected && connected !== undefined) {
      setMountWebsocket(false);

      let reconnectDelay = WEBSOCKET_RECONNECT_DELAY;

      interval = setInterval(() => {
        setMountWebsocket(true);
      }, reconnectDelay);
    }

    return () => {
      if (interval) {
        clearInterval(interval);
      }
    };
  }, [connected]);

  return (
    <WebsocketContext.Provider value={value}>
      {mountWebsocket && <WebsocketService gameUUID={gameUUID} />}
    </WebsocketContext.Provider>
  );
};
