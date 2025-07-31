import { useEffect, useRef } from "react";

const addAuthToWSUrl = (path: string) => {
  const protocol = window.location.protocol === "https:" ? "wss" : "ws";
  return `${protocol}://${window.location.host}${path}?${Telegram.WebApp.initData}`;
};

export const useWebsocketSubscription = (path: string, eventHandler: (event: any) => void) => {
  const websocketRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const websocket = new WebSocket(addAuthToWSUrl(path));
    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log("Websocket connected!");
    };

    websocket.onmessage = (message) => {
      const data = JSON.parse(message.data);
      eventHandler(data);
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
  const sendJSON = (object: object) => {
    let encoded_object = JSON.stringify(object);
    websocketRef.current?.send(encoded_object);
  };
  return { send, sendJSON };
};
