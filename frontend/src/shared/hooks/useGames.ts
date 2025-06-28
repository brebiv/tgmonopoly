import { useQuery } from "@tanstack/react-query";
import type { Game } from "../../entities/types";
import { getGames } from "../api";

export const useGames = (runImmediately = false, enableRetry = false) => {
  return useQuery<Game[], Error>({
    queryKey: ["games"],
    queryFn: getGames,
    enabled: runImmediately,
    retry: enableRetry,
  });
};
