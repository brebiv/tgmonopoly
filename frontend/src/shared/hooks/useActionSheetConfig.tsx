import {
  validateInAuctionAction,
  validatePayRentAction,
  validatePayTaxAction,
} from "@/app/lib/gameActionProcessing/gameActionValidators";
import { useGameStore } from "@/entities/gameStore";
import { GameActionType, PendingActionTypes, type BoardConfig } from "@/entities/types";
import { AcceptActionButton } from "@/features/accept-action/AcceptActionButton";
import { AcceptButton } from "@/features/action-buttons/AcceptButton";
import { RejectButton } from "@/features/action-buttons/RejectButton";
import { StartAuctionButton } from "@/features/auction/StartAuctionButton";
import { RollDiceButton } from "@/features/roll-dice/RollDiceButton";
import { BanknoteIcon, DollarSignIcon, GavelIcon, HandCoinsIcon } from "lucide-react";
import type React from "react";

export const useActionSheetConfig = (
  boardConfig: BoardConfig | undefined,
):
  | { title: string | React.ReactNode; hint: string | React.ReactNode; actions: React.ReactNode[] }
  | undefined => {
  const myPlayer = useGameStore((s) => s.myPlayer);
  const getTileByPosition = useGameStore((s) => s.getTileByPosition);
  const getOwnershipByPosition = useGameStore((s) => s.getOwnershipByPosition);
  const getPlayerById = useGameStore((s) => s.getPlayerById);
  const isCasinoBet = useGameStore((s) => s.isCasinoBet);

  if (!boardConfig) {
    return;
  }

  if (!myPlayer) {
    throw new Error("It shoudn't be this way");
  }

  const pending = myPlayer.pending_action;
  if (!pending) {
    return {
      title: "You don't have any actions",
      hint: "¯\\_(ツ)_/¯",
      actions: [],
    };
  }

  switch (pending.action_type) {
    case PendingActionTypes.ROLL_DICE: {
      if (myPlayer.in_jail) {
        console.warn("Requires improvement. Move harcoded 3 and $100 into BoardConfig setting");
        let escapeAttemptsLeft = 3 - myPlayer.jail_turns;
        let canRollDice = myPlayer.jail_turns < 3;

        return {
          title: "You are in jail!",
          hint: `You have ${escapeAttemptsLeft} escape attempts or you can pay`,
          actions: [
            <RollDiceButton key={GameActionType.ROLL_DICE} disabled={!canRollDice} />,
            <RejectButton key={GameActionType.REJECT} action={GameActionType.REJECT}>
              <HandCoinsIcon /> Pay (${100})
            </RejectButton>,
          ],
        };
      }
      return {
        title: "It's your turn!",
        hint: "You're likely to land on property ______",
        actions: [<RollDiceButton key={GameActionType.ROLL_DICE} />],
      };
    }
    case PendingActionTypes.BUY_PROPERTY: {
      let tile = getTileByPosition(myPlayer.position);
      if (!tile) {
        throw new Error("Could not find tile for player position");
      }

      return {
        title: `Do you want to buy ${tile.name}?`,
        hint: `It would cost $${tile.price}`,
        actions: [
          <AcceptButton key={"accept"}>
            <DollarSignIcon />
            Buy
          </AcceptButton>,
          <StartAuctionButton key={"start_auction"} />,
        ],
      };
    }
    case PendingActionTypes.PAY_RENT: {
      let tile = getTileByPosition(myPlayer.position);
      let ownership = getOwnershipByPosition(myPlayer.position);
      let { rent } = validatePayRentAction(pending);

      if (!tile) {
        throw new Error("Could not find tile for player position");
      }
      if (!ownership) {
        throw new Error("Could not find ownership for player position");
      }
      let player = getPlayerById(ownership?.player);
      if (!player) {
        throw new Error("Could not find player for player ownership");
      }

      return {
        title: (
          <>
            You landed on <span style={{ color: player.color }}>{tile.name}</span>!
          </>
        ),
        hint: `You have to pay rent of $${rent}`,
        actions: [
          <AcceptActionButton key={"accept"}>
            <BanknoteIcon />
            {"Pay"}
          </AcceptActionButton>,
        ],
      };
    }
    case PendingActionTypes.PAY_TAX: {
      let tile = getTileByPosition(myPlayer.position);
      let { amount } = validatePayTaxAction(pending);

      if (!tile) {
        throw new Error("Could not find tile for player position");
      }

      return {
        title: "You have to pay tax!",
        hint: `You have to pay $${amount}`,
        actions: [
          <RejectButton key={"reject"} action={GameActionType.ACCEPT}>
            <BanknoteIcon />
            {"Pay"}
          </RejectButton>,
        ],
      };
    }
    case PendingActionTypes.IN_AUCTION: {
      const { current_price, players } = validateInAuctionAction(pending);
      let title = "Do you want to buy bet?";

      if (players.length == 1) {
        title = "Do you want to buy tile?";
      }

      return {
        title: title,
        hint: `It would cost $${current_price}`,
        actions: [
          <AcceptButton key={"accept"}>
            <GavelIcon />
            Accept
          </AcceptButton>,
          <RejectButton key={"reject"}>Reject</RejectButton>,
        ],
      };
    }
    case PendingActionTypes.IN_CASINO: {
      let hint = "Choose amount that you want to bet";
      if (isCasinoBet) {
        hint = "You can also tap on the coin to accept";
      }
      return {
        title: "You are in casino!",
        hint: hint,
        actions: [
          <AcceptButton
            key={"accept"}
            disabled={!isCasinoBet}
            extraDataFunc={() => {
              const casinoBet = useGameStore.getState().casinoBet;
              return { bet: casinoBet };
            }}
          >
            {"Bet"}
          </AcceptButton>,
          <RejectButton key={"reject"}>Reject</RejectButton>,
        ],
      };
    }
    default:
      return {
        title: "Unknown action",
        hint: "¯\_(ツ)_/¯",
        actions: [],
      };
  }
};
