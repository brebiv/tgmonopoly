import { DICE_ANIMATION_DURATION_SECONDS } from "@/config";
import { useGameStore } from "@/stores/GameStore";
import { useEffect, useRef, useState } from "react";
import ReactDice, { ReactDiceRef } from "react-dice-complete";

function DiceController() {
  const [diceSize, setDiceSize] = useState(0);
  const diceControllerRef = useRef<ReactDiceRef>(null);
  const { dices, showDices } = useGameStore();

  useEffect(() => {
    let screenWidth = window.innerWidth;
    setDiceSize(screenWidth / 6.5);
  }, []);

  useEffect(() => {
    if (dices) {
      rollAll(dices);
    }
  }, [dices]);

  // @ts-ignore
  const rollDone = (totalValue: number, values: number[]) => {
    // console.log("individual die values array:", values);
    // console.log("total dice value:", totalValue);
  };

  const rollAll = (values: number[]) => {
    diceControllerRef.current?.rollAll(values);
  };

  return (
    <div className="dices absolute flex aspect-square w-full items-center justify-center">
      <div
        className="relative z-20 flex h-full w-full items-center justify-center"
        style={{
          visibility: showDices == false ? "hidden" : "visible",
        }}
      >
        <ReactDice
          numDice={2}
          rollTime={DICE_ANIMATION_DURATION_SECONDS}
          dieSize={diceSize}
          // @ts-ignore
          dotColor={window.Telegram.WebApp.themeParams.button_text_color || "black"}
          // @ts-ignore
          faceColor={window.Telegram.WebApp.themeParams.button_color || "white"}
          ref={diceControllerRef}
          rollDone={rollDone}
          disableIndividual={true}
        />
      </div>
    </div>
  );
}

export default DiceController;
