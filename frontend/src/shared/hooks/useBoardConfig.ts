import { useQuery } from "@tanstack/react-query";
import type { BoardConfig } from "../../entities/types";
import { getBoardConfig } from "../api";

export const useBoardConfig = (
  name: string,
  runImmediately = false,
  enableRetry = false
) => {
  return useQuery<BoardConfig, Error>({
    queryKey: ["boardConfig"],
    queryFn: () => getBoardConfig(name),
    enabled: runImmediately,
    retry: enableRetry,
  });
};
