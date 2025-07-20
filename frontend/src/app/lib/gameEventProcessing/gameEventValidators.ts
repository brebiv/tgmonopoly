import type { GameEvent } from "@/entities/types";
import Ajv from "ajv";

export const validateRollDiceEvent = (event: GameEvent): { player: number; dice_values: number[] } => {
  if (!event.extra_data) {
    throw new Error("We are fucked");
  }
  if (!event.extra_data.dice_values || !event.extra_data.player) {
    throw new Error("We are fucked");
  }

  return { player: event.extra_data.player, dice_values: event.extra_data.dice_values };
};

// export const validatePlayerMoveEvent = (event: GameEvent): { player: number; position: number } => {
//   if (!event.extra_data) {
//     throw new Error("We are fucked");
//   }
//   if (!event.extra_data.player || !event.extra_data.position) {
//     throw new Error("We are fucked");
//   }

//   return { player: event.extra_data.player, position: event.extra_data.position };
// };

export const validatePlayerMoveEvent = (
  event: GameEvent,
): {
  player: number;
  position: number;
} => {
  const schema = {
    type: "object",
    required: ["player", "position"],
    additionalProperties: false,
    properties: {
      player: {
        type: "integer",
      },
      position: {
        type: "integer",
      },
    },
  };

  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema);

  if (validate(event.extra_data)) {
  } else {
    console.error("❌ Validation failed:", validate.errors);
    throw new Error(`Validation failed: ${validate.errors}`);
  }

  // @ts-ignore
  return event.extra_data;
};

export const validatePlayerInEvent = (event: GameEvent): { player: number } => {
  if (!event.extra_data) {
    throw new Error("We are fucked");
  }
  if (!event.extra_data.player) {
    throw new Error("We are fucked");
  }

  return { player: event.extra_data.player };
};
