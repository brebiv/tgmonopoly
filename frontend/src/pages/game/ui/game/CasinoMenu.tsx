import { validateInCasinoAction } from "@/app/lib/gameActionProcessing/gameActionValidators";
import { useGameStore } from "@/entities/gameStore";
import type { Player } from "@/entities/types";
import { SelectGroup } from "@/shared/ui/SelectGroup";

import { motion } from "motion/react";
import { useMemo } from "react";
import { CoinController } from "./CoinController";

interface CasinoMenuProps {
  player: Player;
}

export const CasinoMenu = ({ player }: CasinoMenuProps) => {
  const flipCoin = useGameStore((s) => s.flipCoin);
  const isWonCasino = useGameStore((s) => s.isWonCasino);

  const setCasinoBet = useGameStore((s) => s.setCasinoBet);
  const setCasinoIsBet = useGameStore((s) => s.setIsCasinoBet);

  const { pending_action } = player;
  const { available_bets } = useMemo(() => validateInCasinoAction(pending_action!), [pending_action]);

  return (
    <div className="flex h-full w-full flex-col items-center gap-4 px-3 pt-10">
      {isWonCasino != undefined && (
        <div className="absolute top-0 z-20 flex h-full w-full flex-col items-center pt-4">
          <div className="bg-background bg absolute top-0 h-full w-full opacity-80"></div>
          <motion.h1
            initial={{ y: -20, opacity: 0 }}
            animate={{ y: 0, opacity: 100 }}
            transition={{ duration: 0.1 }}
            className="z-10"
          >
            {isWonCasino ? "You won!" : "You lost :("}
          </motion.h1>
        </div>
      )}
      {/* <Coin disabled={!casinoBet} rotation={flipCoin ? 360 * 6 : 0} /> */}
      <CoinController />
      <div className="flex w-full">
        <div className="w-full">
          <SelectGroup
            disabled={flipCoin}
            // defaultValue={available_bets[0]}
            onChange={(value) => {
              setCasinoBet(value);
              setCasinoIsBet(true);
            }}
            className="h-18 gap-1"
            id="bets"
            label="Chose bet:"
          >
            {available_bets.map((bet) => (
              <SelectGroup.Item key={bet} value={bet} className="w-full" />
            ))}
          </SelectGroup>
        </div>
      </div>
    </div>
  );
};
