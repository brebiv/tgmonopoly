import { useReactQuerySubscription } from "@/hooks";
import React, { createContext } from "react";

interface WebsocketContextType {}

const WebsocketContext = createContext<WebsocketContextType | undefined>(undefined);

interface WebsocketContextProviderProps {
  //   children: ReactNode;
}

export const WebsocketContextProvider: React.FC<WebsocketContextProviderProps> = ({}) => {
  const value: WebsocketContextType = {};
  const gameUUID = window.location.pathname.split("/")[2];
  useReactQuerySubscription(gameUUID);

  return <WebsocketContext.Provider value={value}></WebsocketContext.Provider>;
};
