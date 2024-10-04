import { GameEffectType, Tile } from "@/types/api";
import { useEffect, useState } from "react";
import { useTiles } from "@/hooks";
import { useGameStore } from "@/stores/GameStore";
import { getTileFromPosition } from "@/lib/utils";
import BuyPropertyButton from "./BuyPropertyButton";
import RollDiceButton from "./RollDiceButton";

interface MenuContentProps {
  effects: GameEffectType[];
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

    if (firstEffect === GameEffectType.ROLL_DICE) {
      let actions = [
        <RollDiceButton key={0} gameUUID={gameUUID} />,
        //<IncreasePositionButton key={1} />
      ];
      setTitle("It's your turn!");
      setHint("You are likely to land on a property ____");
      setActions(actions);
    } else if (firstEffect === GameEffectType.ASK_BUY) {
      let actions = [<BuyPropertyButton key={0} gameUUID={gameUUID} />];
      setTitle(`Do you want to buy ${currentTile?.name}?`);
      setHint(`It would cost $${currentTile?.propertyData?.price}`);
      setActions(actions);
    }
  }, [effects, currentTile]);

  return (
    <div className="flex flex-col items-center gap-4 px-2 pb-12">
      <div className="flex flex-col items-center gap-1">
        <h1 className="text-2xl font-semibold">{title}</h1>
        <p
          style={{
            color:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.hint_color || "white",
          }}
        >
          {hint}
        </p>
      </div>
      <div className="flex w-full flex-col">{actions}</div>
    </div>
  );
}

export default MenuContent;
