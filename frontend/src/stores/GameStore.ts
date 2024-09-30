import { Player } from "@/types/api";
import { create } from "zustand";

interface GameStore {
  myTurn: boolean;
  setMyTurn: (myTurn: boolean) => void;
  me: Player | null;
  setMe: (me: Player) => void;
}

// @ts-ignore
export const useGameStore = create<GameStore>((set, get) => ({
  myTurn: false,
  setMyTurn: (myTurn: boolean) => {
    set({ myTurn });
  },
  me: null,
  setMe: (me: Player) => {
    set({ me });
  },
}));
