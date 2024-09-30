import { useMutation, useQuery, useQueryClient } from "react-query";
import { createGame, getAuth, getTiles } from "./api";
import React, { useEffect, useRef } from "react";
import { buildGameWebsocketUrl } from "./lib/utils";
import { Game, GameEvent, GameEventScope } from "./types/api";
import { useEventStore } from "./stores/EventStore";
import { useGameStore } from "./stores/GameStore";
import { processGameData } from "./lib/game";

// @ts-ignore
const players = [
  // {
  //   name: "Leo",
  //   cash: 1500,
  //   color: "red",
  //   id: 38,
  //   in_jail: false,
  //   jail_turns: 0,
  //   position: 0,
  //   avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Leo",
  // },
  {
    name: "Anna",
    cash: 1500,
    color: "#918ff7",
    id: 39,
    in_jail: false,
    jail_turns: 0,
    position: 2,
    avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Anna",
  },
  {
    name: "John",
    cash: 1500,
    color: "green",
    id: 40,
    in_jail: false,
    jail_turns: 0,
    position: 5,
    avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=John",
  },
  {
    name: "Emily",
    cash: 1500,
    color: "purple",
    id: 42,
    in_jail: false,
    jail_turns: 0,
    position: 5,
    avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Emily",
  },
  // {
  //   name: "Chris",
  //   cash: 1500,
  //   color: "yellow",
  //   id: 41,
  //   in_jail: false,
  //   jail_turns: 0,
  //   position: 7,
  //   avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Chris",
  // },
  // {
  //   name: "Sophia",
  //   cash: 1500,
  //   color: "orange",
  //   id: 43,
  //   in_jail: false,
  //   jail_turns: 0,
  //   position: 7,
  //   avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Sophia",
  // },
  // {
  //   name: "Michael",
  //   cash: 1500,
  //   color: "pink",
  //   id: 44,
  //   in_jail: false,
  //   jail_turns: 0,
  //   position: 7,
  //   avatar: "https://api.dicebear.com/9.x/pixel-art-neutral/png?seed=Michael",
  // },
];

export const useTiles = () => {
  return useQuery(["tiles"], getTiles, {
    // staleTime: 5 * 60 * 1000, // 5 minutes
    // cacheTime: 10 * 60 * 1000, // 10 minutes
    onSuccess: (data) => {
      // Setting css group colors
      const groupColors = new Set();

      data?.forEach((tile) => {
        if (tile.propertyData?.group_color && tile.propertyData?.group_id) {
          const groupId = tile.propertyData.group_id;

          if (!groupColors.has(groupId)) {
            document.documentElement.style.setProperty(
              `--group-color-${groupId}`,
              tile.propertyData.group_color,
            );
            groupColors.add(groupId);
          }
        }
      });
    },
  });
};

export const useAuth = (runImmediately = false, enableRetry = false) => {
  return useQuery(["me"], getAuth, {
    enabled: runImmediately,
    retry: enableRetry,
  });
};

export const useCreateGame = () => {
  return useMutation({
    mutationFn: createGame,
  });
};

export const useGame = () => {
  return useQuery<Game>({
    queryKey: ["game"],
    enabled: false,
    retry: false,
  });
};

export const usePlayers = () => {
  return useQuery({
    queryKey: ["players"],
    enabled: false,
    retry: false,
  });
};

export const useReactQuerySubscription = (gameUUID: string) => {
  const queryClient = useQueryClient();
  const addEvent = useEventStore((state) => state.addEvent);
  const { setMe, setMyTurn } = useGameStore();

  React.useEffect(() => {
    // const websocket = new WebSocket("wss://echo.websocket.org/");
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));

    websocket.onopen = () => {
      // websocket.send("Hello, Server!");
    };

    websocket.onmessage = (event) => {
      const gameEvent: GameEvent = JSON.parse(event.data);
      console.log("GameEvent", gameEvent);

      let eventScope = gameEvent.type.split(".")[0];

      if (eventScope === GameEventScope.GAME) {
        if (gameEvent.type === "game.connected") {
          queryClient.setQueryData(["game"], () => gameEvent.game);
          // queryClient.setQueryData(["players"], () => gameEvent.players);
          // @ts-ignore
          queryClient.setQueryData(["players"], () => [...gameEvent.players, ...players]);
          setMe(gameEvent.me!);
        } else if (gameEvent.type === "game.action") {
          addEvent(gameEvent);

          const me = useGameStore.getState().me;

          if (gameEvent.game?.current_player == me?.id) {
            setMyTurn(true);
          } else {
            setMyTurn(false);
          }
        }
        console.log("Before processing gameData", gameEvent.game);

        processGameData(gameEvent.game!);
      }
    };

    return () => {
      websocket.close();
    };
  }, [queryClient]);
};

export const usePrevious = (value: any) => {
  const ref = useRef();
  useEffect(() => {
    ref.current = value;
  });
  return ref.current;
};
