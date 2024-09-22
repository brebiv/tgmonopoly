import { useMutation, useQuery } from "react-query";
import { createGame, getGame, getMe, getPlayers, getTiles } from "./api";

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
  return useQuery(["game", gameUuid], () => getGame(gameUuid), {
    enabled: runImmediately,
    retry: enableRetry,
  });
};

export const usePlayers = (
  gameUuid: string,
  runImmediately = false,
  enableRetry = false,
) => {
  return useQuery(["players", gameUuid], () => getPlayers(gameUuid), {
    enabled: runImmediately,
    retry: enableRetry,
  });
};
