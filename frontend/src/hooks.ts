import { useQuery } from "react-query";
import { getTiles } from "./api";

export const useTiles = () => {
  return useQuery(["tiles"], getTiles, {
    // staleTime: 5 * 60 * 1000, // 5 minutes
    // cacheTime: 10 * 60 * 1000, // 10 minutes
  });
};
