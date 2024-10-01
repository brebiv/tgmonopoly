import { Game, Player } from "@/types/api";
import { create } from "zustand";

interface GameStore {
  myTurn: boolean;
  setMyTurn: (myTurn: boolean) => void;
  showTurnMenu: boolean;
  setShowTurnMenu: (showTurnMenu: boolean) => void;
  me: Player | null;
  setMe: (me: Player) => void;
  dices: number[] | null;
  setDices: (dices: number[] | null) => void;
  showDices: boolean;
  setShowDices: (showDices: boolean) => void;
  game: Game | null;
  setGame: (game: Game) => void;
  players: Player[] | null;
  setPlayers: (players: Player[] | null) => void;
  movePlayer: (playerId: number, position: number) => void;
}

// @ts-ignore
export const useGameStore = create<GameStore>((set, get) => ({
  myTurn: false,
  setMyTurn: (myTurn: boolean) => {
    set({ myTurn });
  },
  showTurnMenu: false,
  setShowTurnMenu: (showTurnMenu: boolean) => {
    set({ showTurnMenu });
  },
  me: null,
  setMe: (me: Player) => {
    set({ me });
  },
  dices: null,
  setDices: (dices: number[] | null) => {
    set({ dices });
  },
  showDices: false,
  setShowDices: (showDices: boolean) => {
    set({ showDices });
  },
  game: null,
  setGame: (game: Game) => {
    set({ game });
  },
  players: null,
  setPlayers: (players: Player[] | null) => {
    set({ players });
  },
  movePlayer: (playerId: number, position: number) => {
    const { players, setPlayers } = get();
    if (!players) {
      console.error("Players array is undefined");
      return;
    }
    const newPlayers = [...players];
    const player = newPlayers.find((player) => player.id === playerId);
    if (player) {
      player.position = position;
    } else {
      console.warn(`Player with id ${playerId} not found`);
    }

    setPlayers(newPlayers);
  },
}));
