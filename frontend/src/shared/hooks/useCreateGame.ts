import { useMutation } from "@tanstack/react-query";
import { createGame } from "../api";

export const useCreateGame = () => {
  return useMutation({
    mutationFn: createGame,
  });
};
