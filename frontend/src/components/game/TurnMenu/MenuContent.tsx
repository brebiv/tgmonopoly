import { GameActionType, GameEffect, GameEffectType, Tile } from "@/types/api";
import { useEffect, useState } from "react";
import { useTiles } from "@/hooks";
import { useGameStore } from "@/stores/GameStore";
import { getPropertyById, getTileFromPosition } from "@/lib/utils";
import BuyPropertyButton from "./BuyPropertyButton";
import RollDiceButton from "./RollDiceButton";
import PayRentButton from "./PayRentButton";
import PrisonPayButton from "./PrisonPayButton";
import { MAXIMUM_JAIL_TURNS, PRISON_PAY_AMOUNT } from "@/config";
import { useTheme } from "@/stores/ThemeContext";
import PayButton from "./PayButton";
import CasinoMenuContent from "./CasinoMenuContent";
import { Button } from "@/components/ui/button";
import { sendGameAction } from "@/api";
import { useTradeStore } from "@/stores/TradeStore";
import SendTradeButton from "./SendTradeButton";
import CancelButton from "./CancelButton";
import { GavelIcon } from "lucide-react";
import RejectButton from "./RejectButton";

interface MenuContentProps {
  effects: GameEffect[];
}

function MenuContent({ effects }: MenuContentProps) {
  const gameUUID = window.location.pathname.split("/")[2];
  const [currentTile, setCurrentTile] = useState<Tile | undefined>(undefined);
  const { me, wonCasino, setWonCasino } = useGameStore((state) => state);
  const { data: tiles } = useTiles();
  const firstEffect = effects[0];
  const [title, setTitle] = useState<string>("");
  const [hint, setHint] = useState<string | React.ReactNode>("");
  const [actions, setActions] = useState<React.ReactNode[]>([]);
  const { tradeMenuData, isTradeValid } = useTradeStore();

  const [acceptedCasino, setAcceptedCasino] = useState(false);

  const { hintColor } = useTheme();

  const fireConfetti = async () => {
    // @ts-ignore
    await window.confetti({ ticks: 400 });
    setWonCasino(false);
  };

  useEffect(() => {
    if (tiles && me) {
      setCurrentTile(getTileFromPosition(tiles, me.position));
    }
  }, [tiles, me]);

  useEffect(() => {
    if (wonCasino) {
      fireConfetti();
    }
    return () => {
      // @ts-ignore
      window.confetti.reset();
    };
  }, [wonCasino]);

  useEffect(() => {
    if (!me) {
      return;
    }

    if (firstEffect == undefined) {
      setTitle("It's your turn!, but you have kind of nothing to do");
      setHint("¯\\_(ツ)_/¯");
      setActions([]);
      return;
    }

    if (firstEffect.name !== GameEffectType.IN_CASINO) {
      setAcceptedCasino(false);
    }

    if (firstEffect.name === GameEffectType.ROLL_DICE) {
      let actions = [];
      let title = "";
      let hint = "";

      if (me.in_jail) {
        let usedAllTries = me.jail_turns == MAXIMUM_JAIL_TURNS;
        let dontHaveEnoughCash = me.cash < PRISON_PAY_AMOUNT;
        title = "You are in jail!";

        if (usedAllTries) {
          hint = "You used all tries to escape from jail";
          if (dontHaveEnoughCash) {
            hint += " and don't have enough cash to pay for prison";
          } else {
            hint += ". The only way out of jail is to pay";
          }
        } else {
          hint = `You can roll dices ${MAXIMUM_JAIL_TURNS - me.jail_turns} times`;
        }

        actions = [
          <RollDiceButton key={0} gameUUID={gameUUID} disabled={usedAllTries} />,
          <PrisonPayButton key={1} gameUUID={gameUUID} disabled={dontHaveEnoughCash} />,
        ];
      } else {
        title = "It's your turn!";
        hint = "You are likely to land on a property ____";

        if (me.move_backwards) {
          hint = "You will move backwards this turn";
        }

        actions = [
          //<IncreasePositionButton key={1} />
        ];

        if (tradeMenuData) {
          title = "You are in trade menu!";
          hint = "";

          actions.push(<SendTradeButton key={1} gameUUID={gameUUID} disabled={!isTradeValid()} />);
          actions.push(<CancelButton key={2} />);
        } else {
          actions.push(<RollDiceButton key={0} gameUUID={gameUUID} />);
        }
      }
      setTitle(title);
      setHint(hint);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.ASK_BUY) {
      let actions = [
        <BuyPropertyButton key={0} gameUUID={gameUUID} />,
        <Button
          key={1}
          variant={"destructive"}
          className="w-full gap-2 py-6 text-lg font-semibold"
          onClick={() => {
            sendGameAction({ action: GameActionType.START_AUCTION, game_uuid: gameUUID });
          }}
        >
          <GavelIcon />
          {"Auction"}
        </Button>,
      ];
      setTitle(`Do you want to buy ${currentTile?.name}?`);
      setHint(`It would cost $${firstEffect.effect_data?.price}`);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.PAY_RENT) {
      let actions = [<PayRentButton key={0} gameUUID={gameUUID} />];
      setTitle(`You stepped on other player's property!`);
      setHint(`You have to pay rent of $${firstEffect.effect_data?.rent}`);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.PAY_REPAIRS) {
      let actions = [<PayButton key={0} gameUUID={gameUUID} />];
      setTitle(`You have to repair all houses!`);
      setHint(
        `You have ${firstEffect.effect_data?.number_of_houses} houses\nHouse repair cost is: $${firstEffect.effect_data?.house_repair_cost}\nYou have to pay: $${firstEffect.effect_data?.repair_cost}`,
      );
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.IN_CASINO) {
      let actions = [
        <Button
          key={0}
          variant={"default"}
          className="w-full gap-2 py-6 text-lg font-semibold"
          onClick={() => setAcceptedCasino(true)}
        >
          {"Yes"}
        </Button>,
        <Button
          key={0}
          variant={"destructive"}
          onClick={() => {
            sendGameAction({ action: GameActionType.REJECT, game_uuid: gameUUID });
          }}
          className="w-full gap-2 py-6 text-lg font-semibold"
        >
          {"No"}
        </Button>,
      ];
      setTitle(`Do you want to flip a coin?`);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.IN_TRADE) {
      let actions = [
        <Button
          key={0}
          variant={"default"}
          className="w-full gap-2 py-6 text-lg font-semibold"
          onClick={() => {
            sendGameAction({ action: GameActionType.ACCEPT, game_uuid: gameUUID });
          }}
        >
          {"Yes"}
        </Button>,
        <Button
          key={0}
          variant={"destructive"}
          onClick={() => {
            sendGameAction({ action: GameActionType.REJECT, game_uuid: gameUUID });
          }}
          className="w-full gap-2 py-6 text-lg font-semibold"
        >
          {"No"}
        </Button>,
      ];
      setTitle("Accept trade?");
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.IN_AUCTION) {
      let amountOfPeopleInAuction =
        firstEffect.effect_data!.players_participating_in_auction.length;

      let property = getPropertyById(firstEffect.effect_data!.property);
      let title = `Do you want to bet $${firstEffect.effect_data!.current_auction_price} for ${property!.name}?`;
      let hint = `There are ${amountOfPeopleInAuction} people participating in auction`;

      if (amountOfPeopleInAuction === 1) {
        title = `Do you want to buy ${property!.name} for $${firstEffect.effect_data!.current_auction_price}?`;
        hint = `You can purchase this property without competition`;
      }

      let actions = [
        <Button
          key={0}
          variant={"default"}
          className="w-full gap-2 py-6 text-lg font-semibold"
          onClick={() => {
            sendGameAction({ action: GameActionType.ACCEPT, game_uuid: gameUUID });
          }}
        >
          {amountOfPeopleInAuction > 1 ? "Bet" : "Buy"}
        </Button>,
        <RejectButton key={1} gameUUID={gameUUID} />,
      ];

      setTitle(title);
      setHint(hint);
      setActions(actions);
    } else {
      setTitle("Unknown effect");
    }
  }, [effects, currentTile, me, tradeMenuData]);

  return (
    <div className="flex flex-col items-center gap-4 px-2 pb-12">
      <div className="flex flex-col items-center gap-1">
        <h1 className="text-center text-2xl font-semibold">{title}</h1>
        <p
          className="whitespace-pre-wrap text-center"
          style={{
            color: hintColor,
          }}
        >
          {hint}
        </p>
      </div>
      {acceptedCasino ? (
        <CasinoMenuContent effect={firstEffect} gameUUID={gameUUID} />
      ) : (
        <div className="flex w-full flex-col gap-2">{actions}</div>
      )}
    </div>
  );
}

export default MenuContent;
