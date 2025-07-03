// import { useQuery, useQueryClient } from "@tanstack/react-query";
import { useQueryClient } from "@tanstack/react-query";
import type { GameFrame } from "../../entities/types";
// import { api } from "../api";

// export const getGames = () => {
//   return api
//     .get("/api/games")
//     .then((response) => {
//       return response.data.games;
//     })
//     .catch((error) => {
//       return error.response.data;
//     });
// };

export const useGameFrame = () => {
  const qc = useQueryClient();
  return qc.getQueriesData<GameFrame>({ queryKey: ["gameFrame"] });
  //   return useQuery<GameFrame, Error>({
  //     queryKey: ["gameFrame"],
  //     queryFn: undefined,
  //     enabled: false,
  //     retry: false,
  //   });
};
