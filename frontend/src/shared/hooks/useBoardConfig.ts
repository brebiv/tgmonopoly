import { useQuery } from "@tanstack/react-query";
import type { BoardConfig } from "../../entities/types";
import { getBoardConfig } from "../api";
import { useGameStore } from "@/entities/gameStore";

export const useBoardConfig = (
  name?: string,
  runImmediately = false,
  enableRetry = false,
) => {
  const { game } = useGameStore();

  return useQuery<BoardConfig, Error>({
    queryKey: ["boardConfig"],
    queryFn: () => getBoardConfig(name ? name : game.board_config),
    enabled: runImmediately,
    retry: enableRetry,
    refetchOnWindowFocus: false,
  });
};
