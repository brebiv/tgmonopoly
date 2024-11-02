import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { useTheme } from "@/stores/ThemeContext";
import { GameActionType, GameEffect, GameEffectType } from "@/types/api";
import { useMemo, useState } from "react";
import Coin from "../Casino/Coin";
import { sendGameAction } from "@/api";

function CasinoMenuContent({ effect, gameUUID }: { effect: GameEffect; gameUUID: string }) {
  if (effect.name !== GameEffectType.IN_CASINO) {
    return null;
  }

  const [selectedOption, setSelectedOption] = useState<string>("");

  const canFlipCoin = useMemo(() => {
    return selectedOption !== "";
  }, [selectedOption]);

  const { hintColor } = useTheme();

  return (
    <div className="flex w-full flex-col gap-6 px-4">
      <div className="flex flex-col gap-1">
        <p style={{ color: hintColor }}>{"Select bet"}</p>
        <Select onValueChange={setSelectedOption}>
          <SelectTrigger>
            <SelectValue placeholder="$" />
          </SelectTrigger>
          {/* z-index is so huge because it has to be above modal sheet */}
          <SelectContent className="z-[999999999999]">
            {effect.effect_data?.available_bets.map((bet) => (
              <SelectItem key={bet} value={bet}>
                ${bet}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </div>
      <div className="flex justify-center">
        <Coin
          disabled={!canFlipCoin}
          onClick={() => {
            if (canFlipCoin) {
              sendGameAction({
                action: GameActionType.ACCEPT,
                game_uuid: gameUUID,
                extra_data: {
                  bet_amount: selectedOption,
                },
              });
            }
          }}
        />
      </div>
    </div>
  );
}

export default CasinoMenuContent;
