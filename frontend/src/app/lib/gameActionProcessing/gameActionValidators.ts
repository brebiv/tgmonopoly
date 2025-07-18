import { Ajv } from "ajv";
import type { PendingAction } from "@/entities/types";

export const validateInAuctionAction = (
  pendingAction: PendingAction,
): {
  property_id: number;
  current_price: number;
  next_price: number;
  started_by_id: number;
  players: number[];
  is_bet: boolean;
} => {
  if (!pendingAction.action_data) {
    throw new Error("We are fucked");
  }

  const schema = {
    type: "object",
    required: ["property_id", "current_price", "next_price", "started_by_id", "players", "is_bet"],
    additionalProperties: false,
    properties: {
      property_id: { type: "integer" },
      current_price: { type: "integer" },
      next_price: { type: ["integer", "null"] },
      started_by_id: { type: "integer" },
      players: {
        type: "array",
        items: { type: "integer" },
      },
      is_bet: { type: "boolean" },
    },
  };

  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema);

  if (validate(pendingAction.action_data)) {
  } else {
    console.error("❌ Validation failed:", validate.errors);
    throw new Error(`Validation failed: ${validate.errors}`);
  }

  // @ts-ignore
  return pendingAction.action_data;
};

export const validatePayRentAction = (
  pendingAction: PendingAction,
): {
  rent: number;
} => {
  if (!pendingAction.action_data) {
    throw new Error("We are fucked");
  }

  const schema = {
    type: "object",
    required: ["rent"],
    additionalProperties: false,
    properties: {
      rent: { type: "integer" },
    },
  };

  const ajv = new Ajv({ allErrors: true });
  const validate = ajv.compile(schema);

  if (validate(pendingAction.action_data)) {
  } else {
    console.error("❌ Validation failed:", validate.errors);
    throw new Error(`Validation failed: ${validate.errors}`);
  }

  // @ts-ignore
  return pendingAction.action_data;
};
