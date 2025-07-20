import type { StateCreator } from "zustand";
import type { GameState } from "@/entities/gameStore";
import { GameEventTypes, type GameEvent } from "@/entities/types";
import { sleep } from "@/shared/utils";
import { COIN_FLIP_DURATION_MS, DICE_ROLL_DURATION_MS, PLAYER_CHIP_MOVE_DURATION_MS } from "@/shared/config";
import { validatePlayerInEvent, validatePlayerMoveEvent, validateRollDiceEvent } from "./gameEventValidators";

type Set = Parameters<StateCreator<GameState>>[0];
type Get = Parameters<StateCreator<GameState>>[1];

export const processEvent = async (event: GameEvent, set: Set, get: Get) => {
  console.log("Processing event", event);
  if (event.event_type === GameEventTypes.PLAYER_ROLL_DICE) {
    let { dice_values } = validateRollDiceEvent(event);
    set({ dices: dice_values, showDices: true });
    await sleep(DICE_ROLL_DURATION_MS);
  } else if (event.event_type === GameEventTypes.PLAYER_MOVE) {
    let { player: playerID, position: newPosition } = validatePlayerMoveEvent(event);
    let player = get().players.find((p) => p.id === playerID);

    if (!player) {
      throw new Error("We are fucked");
    }

    set((state) => ({
      players: state.players.map((p) => (p.id === player.id ? { ...p, position: newPosition } : p)),
    }));
    await sleep(PLAYER_CHIP_MOVE_DURATION_MS);
    set({ showDices: false });
  } else if (event.event_type === GameEventTypes.PLAYER_WON_CASINO) {
    let { player: playerID } = validatePlayerInEvent(event);
    let player = get().players.find((p) => p.id === playerID);

    set(() => ({
      flipCoin: true,
      casinoPlayer: player,
    }));

    await sleep(COIN_FLIP_DURATION_MS);
    set(() => ({
      isWonCasino: true,
    }));
    await sleep(1500);
  } else if (event.event_type === GameEventTypes.PLAYER_LOST_CASINO) {
    let { player: playerID } = validatePlayerInEvent(event);
    let player = get().players.find((p) => p.id === playerID);

    set(() => ({
      flipCoin: true,
      casinoPlayer: player,
    }));

    await sleep(COIN_FLIP_DURATION_MS);

    set(() => ({
      isWonCasino: false,
    }));
    await sleep(1500);
  }
  console.log("Done processing event", event);
};
