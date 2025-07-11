// import { useGameStore } from "@/entities/gameStore";
import { useEffect, useRef } from "react";
import { buildGameWebsocketUrl } from "../utils";

export const useReactQuerySubscription = (gameUUID: string) => {
  const websocketRef = useRef<WebSocket | null>(null);
  // const { processGameFrame } = useGameStore();
  // const queryClient = useQueryClient();

  useEffect(() => {
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));
    websocketRef.current = websocket;

    websocket.onopen = () => {
      console.log("Websocket connected!");
    };

    websocket.onmessage = (message) => {
      const data = JSON.parse(message.data);
      console.log(data);

      // processGameFrame(data);
      // const queryKey =
      // queryClient.setQueryData(["gameFrame"], () => data);
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
