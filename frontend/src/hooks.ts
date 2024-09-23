import { useMutation, useQuery, useQueryClient } from "react-query";
import { createGame, getGame, getMe, getPlayers, getTiles } from "./api";
import React from "react";
import { buildGameWebsocketUrl } from "./lib/utils";
import { GameEvent, GameEventScope } from "./types/api";

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

export const useMe = (runImmediately = false, enableRetry = false) => {
  return useQuery(["me"], getMe, {
    enabled: runImmediately,
    retry: enableRetry,
  });
};

export const useCreateGame = () => {
  return useMutation({
    mutationFn: createGame,
  });
};

export const useGame = (
  gameUuid: string,
  runImmediately = false,
  enableRetry = false,
) => {
  return useQuery({
    queryKey: ["game"],
    enabled: false,
    retry: false,
  });
};

export const usePlayers = (
  gameUuid: string,
  runImmediately = false,
  enableRetry = false,
) => {
  return useQuery({
    queryKey: ["players"],
    enabled: false,
    retry: false,
  });
};

export const useReactQuerySubscription = (gameUUID: string) => {
  const queryClient = useQueryClient();

  React.useEffect(() => {
    // const websocket = new WebSocket("wss://echo.websocket.org/");
    const websocket = new WebSocket(buildGameWebsocketUrl(gameUUID));

    websocket.onopen = () => {
      // websocket.send("Hello, Server!");
    };

    websocket.onmessage = (event) => {
      const gameEvent: GameEvent = JSON.parse(event.data);

      let eventScope = gameEvent.type.split(".")[0];

      if (eventScope === GameEventScope.GAME) {
        if (gameEvent.type === "game.connected") {
          queryClient.setQueryData(["game"], () => gameEvent.game);
          queryClient.setQueryData(["players"], () => gameEvent.players);
        }
      }

      // const queryKey = ["game"];
      // // queryClient.setQueryData(queryKey, (oldData) => {
      // queryClient.setQueryData(queryKey, () => {
      //   return {
      //     game: JSON.parse(event.data),
      //     // ...oldData,
      //     // ...data,
      //   };
      // });
    };

    return () => {
      websocket.close();
    };
  }, [queryClient]);
};
