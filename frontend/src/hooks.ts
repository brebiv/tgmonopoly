import { useMutation, useQuery, useQueryClient, UseQueryResult } from "react-query";
import { createGame, getAuth, getGames, getTiles } from "./api";
import { useEffect, useRef, useState } from "react";
import { buildGameWebsocketUrl } from "./lib/utils";
import { Game, GameFrame, GameEventScope, Ownership, GamesResponse } from "./types/api";
import { useEventStore } from "./stores/EventStore";
import { useGameStore } from "./stores/GameStore";
import { processGameData } from "./lib/game";
import { TGInitParams } from "./types/telegram";
import { useWebsocketStore } from "./stores/WebsocketStore";

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

export const useOwnerships = (): UseQueryResult<Ownership[] | null> => {
  return useQuery({
    queryKey: ["ownerships"],
    enabled: false,
    retry: false,
  });
};

export const useReactQuerySubscription = (gameUUID: string) => {
  const queryClient = useQueryClient();
  const { addEvents, processGameFrame } = useEventStore((state) => state);
  const { setMe, setGame, setPlayers, setOwnerships } = useGameStore();
  const { setConnected } = useWebsocketStore();

  useEffect(() => {
    // const websocket = new WebSocket("wss://echo.websocket.org/");
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));

    websocket.onopen = () => {
      setConnected(true);
      // websocket.send("Hello, Server!");
    };

    websocket.onmessage = (event) => {
      const gameFrame: GameFrame = JSON.parse(event.data);
      console.log("GameEvent", gameFrame);

      let eventScope = gameFrame.type.split(".")[0];

      if (eventScope === GameEventScope.GAME) {
        if (gameFrame.type === "game.connected") {
          queryClient.setQueryData(["game"], () => gameFrame.game);
          queryClient.setQueryData(["players"], () => gameFrame.players);
          queryClient.setQueryData(["ownerships"], () => gameFrame.ownerships);
          // queryClient.setQueryData(["players"], () => [...gameFrame.players, ...players]);
          setPlayers(gameFrame.players!);
          setGame(gameFrame.game!);
          setMe(gameFrame.me!);
          setOwnerships(gameFrame.ownerships!);
          processGameFrame(gameFrame);
        } else if (gameFrame.type === "game.action") {
          queryClient.setQueryData(["game"], () => gameFrame.game);
          queryClient.setQueryData(["players"], () => gameFrame.players);
          queryClient.setQueryData(["ownerships"], () => gameFrame.ownerships);
          // queryClient.setQueryData(["players"], () => [...gameFrame.players, ...players]);
        }
        processGameData(gameFrame.game!);
        if (gameFrame.events) {
          addEvents(gameFrame.events);
        }
      }
    };

    websocket.onclose = (event) => {
      setConnected(false);
      event.wasClean;
      console.log("Connection closed");
    };

    return () => {
      websocket.close();
    };
  }, [queryClient]);
};

type UsePreviousType<T> = T | undefined;

export const usePrevious = <T>(value: T): UsePreviousType<T> => {
  const ref = useRef<UsePreviousType<T>>();
  useEffect(() => {
    ref.current = value;
  }, [value]);
  return ref.current;
};

export const useTelegramInitParams = (): TGInitParams | null => {
  const [initParams, setInitParams] = useState<TGInitParams | null>(null);

  useEffect(() => {
    // @ts-ignore
    setInitParams(window.Telegram.WebView.initParams as TGInitParams);
  }, []);

  return initParams;
};

export const useGames = (runImmediately = false, enableRetry = false) => {
  return useQuery<GamesResponse, Error>(["games"], getGames, {
    enabled: runImmediately,
    retry: enableRetry,
  });
};
