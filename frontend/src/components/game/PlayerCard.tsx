import { Player } from "@/types/api";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Card, CardContent } from "../ui/card";
import { useEffect, useState } from "react";
import { useGame, usePrevious } from "@/hooks";
import { Dices } from "lucide-react";
import { CASH_GAIN_ANIMATION_DURATION_SECONDS, CASH_LOSS_ANIMATION_DURATION_SECONDS, PLAYER_CHIP_COLORS } from "@/config";

type PlayerCardProps = {
  player: Player;
};

function PlayerCard({ player }: PlayerCardProps) {
  const { data: game } = useGame();
  const [isCurrentPlayer, setIsCurrentPlayer] = useState(false);
  const [primaryColor, _] = PLAYER_CHIP_COLORS[player.color as keyof typeof PLAYER_CHIP_COLORS];
  const [cashLoss, setCashLoss] = useState(0);
  const [cashGain, setCashGain] = useState(0);

  const previousPlayer = usePrevious(player);

  useEffect(() => {
    if (game) {
      if (game.current_player == player.id) {
        setIsCurrentPlayer(true);
      } else {
        setIsCurrentPlayer(false);
      }
      if (previousPlayer) {
        if (previousPlayer.cash > player.cash) {
          setCashLoss(previousPlayer.cash - player.cash);
        } else if (previousPlayer.cash < player.cash) {
          setCashGain(player.cash - previousPlayer.cash);
        }
      }
    }
  }, [game]);

  useEffect(() => {
    if (cashLoss > 0) {
      const timer = setTimeout(() => {
        setCashLoss(0);
      }, CASH_LOSS_ANIMATION_DURATION_SECONDS * 1000);
      return () => clearTimeout(timer);
    }
  }, [cashLoss]);

  useEffect(() => {
    if (cashGain > 0) {
      const timer = setTimeout(() => {
        setCashGain(0);
      }, CASH_GAIN_ANIMATION_DURATION_SECONDS * 1000);
      return () => clearTimeout(timer);
    }
  }, [cashGain]);

  return (
    <Card className="relative">
      <CardContent className="flex gap-2 p-2">
        <Avatar
          className="border-2"
          style={{
            borderColor: primaryColor || "black",
          }}
        >
          <AvatarImage src={player.avatar} />
          <AvatarFallback>o_o</AvatarFallback>
        </Avatar>
        <div className="h-full w-full">
          <p className="text-sm">
            {player.name} {player.id}
          </p>
          {cashLoss > 0 && (
            <p
              className="flying-text absolute z-20 text-sm font-bold text-[#f02b2b]"
              style={{
                animationDuration: `${CASH_LOSS_ANIMATION_DURATION_SECONDS}s`,
              }}
            >
              - {cashLoss}
            </p>
          )}
          {cashGain > 0 && (
            <p
              className="flying-text absolute z-20 text-sm font-bold text-[#28a745]"
              style={{
                animationDuration: `${CASH_GAIN_ANIMATION_DURATION_SECONDS}s`,
                animationDirection: "reverse",
              }}
            >
              + {cashGain}
            </p>
          )}
          <p
            className="text-sm font-thin"
            style={{
              color:
                // @ts-ignore
                window.Telegram.WebApp.themeParams.hint_color || "white",
            }}
          >
            $ {player.cash}
          </p>
        </div>
      </CardContent>
      <div className="absolute right-0 top-0">{isCurrentPlayer && <Dices />}</div>
    </Card>
  );
}

export default PlayerCard;