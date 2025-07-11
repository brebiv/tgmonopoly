import type { StateCreator } from "zustand";
import type { GameState } from "@/entities/gameStore";
import { GameEventTypes, type GameEvent } from "@/entities/types";
import { sleep } from "@/shared/utils";
import { PLAYER_CHIP_MOVE_DURATION_MS } from "@/shared/config";
import { validatePlayerMove } from "./gameEventValidators";

type Set = Parameters<StateCreator<GameState>>[0];
type Get = Parameters<StateCreator<GameState>>[1];

export const processEvent = async (event: GameEvent, set: Set, get: Get) => {
  console.log("Processing event", event);
  switch (event.event_type) {
    case GameEventTypes.PLAYER_ROLL_DICE:
      await sleep(1000);
      break;
    case GameEventTypes.PLAYER_MOVE:
      let { player: playerID, position: newPosition } = validatePlayerMove(event);
      let player = get().players.find((p) => p.id === playerID);

      if (!player) {
        throw new Error("We are fucked");
      }

      set((state) => ({
        players: state.players.map((p) => (p.id == player.id ? { ...p, position: newPosition } : p)),
      }));
      await sleep(PLAYER_CHIP_MOVE_DURATION_MS);
  }
  console.log("Done processing event", event);
};
