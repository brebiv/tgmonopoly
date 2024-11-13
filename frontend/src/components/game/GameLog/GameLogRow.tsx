import { usePlayers, useTiles } from "@/hooks";
import { getPlayerByIdDepricated, getTileFromId } from "@/lib/utils";
import { ChanceCardType, GameActionType, GameEvent, GameEventType } from "@/types/api";
import PlayerNameSpan from "./PlayerNameSpan";

const IGNORABLE_EVENTS = [GameActionType.START_GAME, GameActionType.MOVE_PLAYER];

function GameLogRow({ event }: { event: GameEvent }) {
  let message: string | React.ReactNode = "Unknown action: " + event.action;
  const { data: players = [] } = usePlayers();
  const { data: tiles = [] } = useTiles();

  // @ts-ignore
  if (IGNORABLE_EVENTS.includes(event.action!)) {
    return null;
  }

  // @ts-ignore
  const player = getPlayerByIdDepricated(players, event.player);

  switch (event.action) {
    case GameActionType.ROLL_DICE:
      message = "Rolled dice and got " + event.dices!.join(":");
      break;
    case GameActionType.PASSED_START:
      message = "Moved though the start and got bonus of $" + event.amount!;
      break;
    case GameActionType.GO_TO_CASINO:
      message = "Deciding to bet or not to bet in the casino";
      break;
    case GameEventType.REJECT_CASINO:
      message = "Decided not to bet in the casino";
      break;
    case GameEventType.WON_CASINO:
      message = `Won $${event.amount} the casino bet`;
      break;
    case GameEventType.LOST_CASINO:
      message = `Lost $${event.amount} in the casino`;
      break;
    case GameEventType.BUY_PROPERTY:
      let tile = getTileFromId(tiles, event.tile!);
      message = (
        <p>
          {"Bought property"}{" "}
          <span style={{ color: `var(--group-color-${tile!.propertyData?.group_id})` }}>
            {tile?.name}
          </span>{" "}
          for ${tile?.propertyData?.price}
        </p>
      );
      break;
    case GameEventType.GO_TO_PRISON:
      message = "Got in jail";
      break;
    case GameEventType.PAY_FOR_PRISON:
      message = "Payed to get out of jail";
      break;
    case GameEventType.PRISON_RELEASE_FAIL:
      if (event.tries_left === 0) {
        message = "Used all tries to escape from jail, now he can only pay to get out";
      } else {
        message = `Failed to get out of jail. He can try to escape jail ${event.tries_left} more time(s)`;
      }
      break;
    case GameEventType.RELEASE_FROM_PRISON:
      message = "Escaped from jail";
      break;
    case GameEventType.CHANCE_CARD:
      if (event.chance_card_data!.card_type === ChanceCardType.MOVE_BACKWARDS) {
        message = `Stepped on chance card, next turn he will move backwards`;
      } else if (event.chance_card_data!.card_type === ChanceCardType.REPAIRS) {
        message = `Stepped on chance card, he has to repair all of his properties`;
      } else {
        message = "Unknown chance card action";
      }
      break;
    case GameEventType.STEPPED_ON_OWN_PROPERTY:
      message = "Landed on own property";
      break;
    case GameEventType.PAY_RENT:
      message = (
        <p>
          Payed ${event.amount} in rent to <PlayerNameSpan player={event.to_player!} />
        </p>
      );
      break;
    case GameEventType.PAY_TO_BANK:
      message = `Payed ${event.amount} to bank`;
      break;
  }

  return (
    <p>
      <PlayerNameSpan player={player!} />: {message}
    </p>
  );
}

export default GameLogRow;
