import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { cn, getPlayerById, sleep } from "@/lib/utils";
import { useGameStore } from "@/stores/GameStore";
import { useTheme } from "@/stores/ThemeContext";
import { useTradeStore } from "@/stores/TradeStore";
import { ExitIcon } from "@radix-ui/react-icons";
import { useEffect, useMemo, useState } from "react";

interface AddMoneyToTradeDialogProps {
  open: boolean;
  setOpen: (open: boolean) => void;
  isGivingMoney: boolean;
}

function AddMoneyToTradeDialog({ open, setOpen, isGivingMoney }: AddMoneyToTradeDialogProps) {
  const [money, setMoney] = useState(0);
  const [errorMessage, setErrorMessage] = useState("");
  const { me } = useGameStore();
  const { destructiveTextColor } = useTheme();

  const { setCashGiven, setCashReceived: setCashRecieved, tradeMenuData } = useTradeStore();

  const toPlayer = useMemo(() => getPlayerById(tradeMenuData?.to_player!), [tradeMenuData]);
  let playerThatGivesMoney = me;

  if (!isGivingMoney) {
    playerThatGivesMoney = toPlayer!;
  }

  useEffect(() => {
    async function resetMoney() {
      // because of duration-300
      await sleep(300);
      setMoney(0);
      setErrorMessage("");
    }
    if (!open) {
      resetMoney();
    } else {
      if (tradeMenuData) {
        if (isGivingMoney) {
          setMoney(tradeMenuData.cash_given || 0);
        } else {
          setMoney(tradeMenuData.cash_received || 0);
        }
      }
    }
  }, [open]);

  return (
    <div
      className={cn(
        "absolute top-0 flex h-full w-full flex-col items-center gap-2 bg-black bg-opacity-90 p-3 transition-all duration-300 ease-in-out",
        open ? "opacity-100" : "pointer-events-none opacity-0",
      )}
    >
      <div className="flex w-full">
        <h2 className="text-center">{"Add money to trade"}</h2>
        <Button
          variant={"destructive"}
          className="ml-auto h-auto gap-1 p-1"
          onClick={() => setOpen(false)}
        >
          Back
          <ExitIcon />
        </Button>
      </div>
      <Input
        className="w-full"
        style={{ borderColor: errorMessage ? destructiveTextColor : "" }}
        type="number"
        onChange={(e) => {
          const value = e.target.value;
          const parsedValue = Number(value);
          setMoney(parsedValue);

          if (parsedValue > playerThatGivesMoney!.cash) {
            setErrorMessage("You don't have enough cash");
          } else {
            setErrorMessage("");
          }
        }}
        value={money}
        min={0}
        max={playerThatGivesMoney?.cash}
        placeholder="0"
      />
      <div className="grid w-full grid-cols-4 gap-2">
        <Button
          className="gap-1 transition-all"
          onClick={() => setMoney(money + 10)}
          disabled={money + 10! > playerThatGivesMoney?.cash!}
        >
          +10
        </Button>
        <Button
          className="gap-1 transition-all"
          onClick={() => setMoney(money + 20)}
          disabled={money + 20! > playerThatGivesMoney?.cash!}
        >
          +20
        </Button>
        <Button
          className="gap-1 transition-all"
          onClick={() => setMoney(money + 50)}
          disabled={money + 50! > playerThatGivesMoney?.cash!}
        >
          +50
        </Button>
        <Button
          className="gap-1 transition-all"
          onClick={() => setMoney(money + 100)}
          disabled={money + 100! > playerThatGivesMoney?.cash!}
        >
          +100
        </Button>
      </div>
      <Button
        variant={"default"}
        className="w-full transition-all"
        disabled={
          money === 0 || isNaN(money) || errorMessage !== "" || money > playerThatGivesMoney?.cash!
        }
        onClick={() => {
          const amount = Number.isNaN(money) ? 0 : money;
          if (amount === 0) {
            return;
          }

          if (isGivingMoney) {
            setCashGiven(amount);
          } else {
            setCashRecieved(amount);
          }
          setOpen(false);
        }}
      >
        {"Add money"}
      </Button>
    </div>
  );
}

export default AddMoneyToTradeDialog;
