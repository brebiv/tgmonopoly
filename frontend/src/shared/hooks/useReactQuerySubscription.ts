import { useEffect, useRef } from "react";

const buildGameWebsocketUrl = (gameUUID: string) => {
  const path = "ws/game/" + gameUUID;
  const protocol = "ws";

  return `${protocol}://${window.location.host}/${path}/?${Telegram.WebApp.initData}`;
};

export const useReactQuerySubscription = (gameUUID: string) => {
  const websocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));
    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log("Websocket connected!");
    };

    websocket.onmessage = (message) => {
      console.log(message.data);
    };

    websocket.onclose = () => {
      console.log("Websocket closed");
    };

    return () => {
      websocket.close();
    };
  }, []);

  const send = (text: string) => {
    websocketRef.current?.send(text);
  };
  return { send };
};
