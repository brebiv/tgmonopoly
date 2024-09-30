import { RefObject, useEffect, useRef, useState } from "react";
import ReactDice, { ReactDiceRef } from "react-dice-complete";

// @ts-ignore
interface DiceControllerProps {
  diceControllerRef: RefObject<ReactDiceRef>;
}

function DiceController() {
  const [diceSize, setDiceSize] = useState(0);
  const diceControllerRef = useRef<ReactDiceRef>(null);

  useEffect(() => {
    let screenWidth = window.innerWidth;
    setDiceSize(screenWidth / 6.5);
  }, []);

  // @ts-ignore
  const rollDone = (totalValue: number, values: number[]) => {
    // console.log("individual die values array:", values);
    // console.log("total dice value:", totalValue);
  };

  // @ts-ignore
  const rollAll = () => {
    diceControllerRef.current?.rollAll();
  };

  return (
    <div className="dices absolute z-10 flex aspect-square w-full items-center justify-center">
      <div className="relative flex h-full w-full items-center justify-center">
        <ReactDice
          numDice={2}
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
