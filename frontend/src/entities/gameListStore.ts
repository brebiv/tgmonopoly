import { create } from "zustand";
import { devtools } from "zustand/middleware";
import type { Game } from "./types";

type GameList = {
  games: Game[];
  setGames: (games: Game[]) => void;
};

export const useGameListStore = create<GameList>()(
  devtools((set) => ({
    games: [],
    setGames: (games) => set({ games: games }),
  }))
);
