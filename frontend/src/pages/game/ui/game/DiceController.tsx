import ReactDice, { type ReactDiceRef } from "react-dice-complete";
import cn from "classnames";

import { useGameStore } from "@/entities/gameStore";
import { DICE_ROLL_DURATION_MS } from "@/shared/config";
import { useEffect, useRef } from "react";

export const DiceController = () => {
  const reactDice = useRef<ReactDiceRef>(null);
  const dices = useGameStore((s) => s.dices);
  const showDices = useGameStore((s) => s.showDices);

  const rollAll = (values: number[]) => {
    if (reactDice.current) {
      reactDice.current?.rollAll(values);
    } else {
      console.warn("react dice is not initialized");
    }
  };

  useEffect(() => {
    if (dices && reactDice.current) {
      rollAll(dices);
    }
  }, [dices]);

  return (
    <div
      className={cn("absolute flex h-full w-full items-center justify-center", {
        invisible: !showDices,
      })}
    >
      <ReactDice
        ref={reactDice}
        numDice={2}
        rollDone={() => {}}
        faceColor={Telegram.WebApp.themeParams.button_color}
        dotColor={Telegram.WebApp.themeParams.button_text_color}
        rollTime={DICE_ROLL_DURATION_MS / 1000}
        disableIndividual
      />
    </div>
  );
};
