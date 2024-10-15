import { GameEffect, GameEffectType, Tile } from "@/types/api";
import { useEffect, useState } from "react";
import { useTiles } from "@/hooks";
import { useGameStore } from "@/stores/GameStore";
import { getTileFromPosition } from "@/lib/utils";
import BuyPropertyButton from "./BuyPropertyButton";
import RollDiceButton from "./RollDiceButton";
import PayRentButton from "./PayRentButton";
import PrisonPayButton from "./PrisonPayButton";
import { MAXIMUM_JAIL_TURNS, PRISON_PAY_AMOUNT } from "@/config";

interface MenuContentProps {
  effects: GameEffect[];
}

function MenuContent({ effects }: MenuContentProps) {
  const gameUUID = window.location.pathname.split("/")[2];
  const [currentTile, setCurrentTile] = useState<Tile | undefined>(undefined);
  const { me } = useGameStore((state) => state);
  const { data: tiles } = useTiles();
  const firstEffect = effects[0];
  const [title, setTitle] = useState<string>("");
  const [hint, setHint] = useState<string>("");
  const [actions, setActions] = useState<React.ReactNode[]>([]);

  useEffect(() => {
    if (tiles && me) {
      setCurrentTile(getTileFromPosition(tiles, me.position));
    }
  }, [tiles, me]);

  useEffect(() => {
    console.log("effects", effects);
    console.log("me", me);

    if (firstEffect == undefined) {
      setTitle("It's your turn!, but you have kind of nothing to do");
      setHint("¯\\_(ツ)_/¯");
      setActions([]);
      return;
    }

    if (firstEffect.name === GameEffectType.ROLL_DICE) {
      let actions = [];
      let title = "";
      let hint = "";

      if (me?.in_jail) {
        let usedAllTries = me?.jail_turns == MAXIMUM_JAIL_TURNS;
        let dontHaveEnoughCash = me?.cash < PRISON_PAY_AMOUNT;
        title = "You are in jail!";

        if (usedAllTries) {
          hint = "You used all tries to escape from jail";
          if (dontHaveEnoughCash) {
            hint += " and don't have enough cash to pay for prison";
          } else {
            hint += ". The only way out of jail is to pay";
          }
        } else {
          hint = `You can roll dices ${MAXIMUM_JAIL_TURNS - me?.jail_turns} times`;
        }

        actions = [
          <RollDiceButton key={0} gameUUID={gameUUID} disabled={usedAllTries} />,
          <PrisonPayButton key={1} gameUUID={gameUUID} disabled={dontHaveEnoughCash} />,
        ];
      } else {
        title = "It's your turn!";
        hint = "You are likely to land on a property ____";
        actions = [
          <RollDiceButton key={0} gameUUID={gameUUID} />,
          //<IncreasePositionButton key={1} />
        ];
      }
      setTitle(title);
      setHint(hint);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.ASK_BUY) {
      let actions = [<BuyPropertyButton key={0} gameUUID={gameUUID} />];
      setTitle(`Do you want to buy ${currentTile?.name}?`);
      setHint(`It would cost $${firstEffect.effect_data?.price}`);
      setActions(actions);
    } else if (firstEffect.name === GameEffectType.PAY_RENT) {
      let actions = [<PayRentButton key={0} gameUUID={gameUUID} />];
      setTitle(`You stepped on other player's property!`);
      setHint(`You have to pay rent of $${firstEffect.effect_data?.rent}`);
      setActions(actions);
    }
  }, [effects, currentTile]);

  return (
    <div className="flex flex-col items-center gap-4 px-2 pb-12">
      <div className="flex flex-col items-center gap-1">
        <h1 className="text-center text-2xl font-semibold">{title}</h1>
        <p
          className="text-center"
          style={{
            color:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.hint_color || "white",
          }}
        >
          {hint}
        </p>
      </div>
      <div className="flex w-full flex-col gap-2">{actions}</div>
    </div>
  );
}

export default MenuContent;
