import { useQuery } from "@tanstack/react-query";
import type { Me } from "../../entities/types";
import { getAuth } from "../api";

export const useMe = (runImmediately = false, enableRetry = false) => {
  return useQuery<Me, Error>({
    queryKey: ["me"],
    queryFn: getAuth,
    enabled: runImmediately,
    retry: enableRetry,
  });
};
