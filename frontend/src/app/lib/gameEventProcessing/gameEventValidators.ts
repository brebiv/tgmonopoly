import type { GameEvent } from "@/entities/types";

export const validateRollDiceEvent = (event: GameEvent): { player: number; dice_values: number[] } => {
  if (!event.extra_data) {
    throw new Error("We are fucked");
  }
  if (!event.extra_data.dice_values || !event.extra_data.player) {
    throw new Error("We are fucked");
  }

  return { player: event.extra_data.player, dice_values: event.extra_data.dice_values };
};

export const validatePlayerMoveEvent = (event: GameEvent): { player: number; position: number } => {
  if (!event.extra_data) {
    throw new Error("We are fucked");
  }
  if (!event.extra_data.player || !event.extra_data.position) {
    throw new Error("We are fucked");
  }

  return { player: event.extra_data.player, position: event.extra_data.position };
};
