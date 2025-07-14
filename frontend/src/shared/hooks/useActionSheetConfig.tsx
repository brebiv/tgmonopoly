import { useGameStore } from "@/entities/gameStore";
import { GameActionType, PendingActionTypes, type BoardConfig } from "@/entities/types";
import { BuyButton } from "@/features/buy-property/BuyPropertyButton";
import { RollDiceButton } from "@/features/roll-dice/RollDiceButton";
import type React from "react";

export const useActionSheetConfig = (
  boardConfig: BoardConfig | undefined,
  // @ts-ignore
  showActionSheet: boolean, // for trigerring rerenders
): { title: string; hint: string; actions: React.ReactNode[] } | undefined => {
  const { myPlayer, getTileByPosition } = useGameStore();

  if (!boardConfig) {
    return;
  }

  if (!myPlayer) {
    throw new Error("It shoudn't be this way");
  }

  const pending = myPlayer.pending_actions[0];
  if (!pending) {
    // console.log("There is no pending action for this player");
    return {
      title: "You don't have any actions",
      hint: "¯\_(ツ)_/¯",
      actions: [],
    };
  }

  switch (pending.action_type) {
    case PendingActionTypes.ROLL_DICE:
      return {
        title: "It's your turn!",
        hint: "You're likely to land on property ______",
        actions: [<RollDiceButton key={GameActionType.ROLL_DICE} />],
      };
    case PendingActionTypes.BUY_PROPERTY:
      let tile = getTileByPosition(myPlayer.position);
      if (!tile) {
        throw new Error("Could not find tile for player position");
      }

      return {
        title: `Do you want to buy ${tile.name}?`,
        hint: `It would cost $${tile.price}`,
        actions: [<BuyButton key={"buy"} myPlayer={myPlayer} propertyTile={tile} />],
      };
    default:
      return {
        title: "Unknown action",
        hint: "¯\_(ツ)_/¯",
        actions: [],
      };
  }
};
