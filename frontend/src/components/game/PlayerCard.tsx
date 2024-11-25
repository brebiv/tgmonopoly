import { GameEffect, Player, PlayerStatus } from "@/types/api";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Card, CardContent } from "../ui/card";
import { useEffect, useState } from "react";
import { useGame, usePrevious } from "@/hooks";
import { Dices, FlagIcon, HandshakeIcon, Skull } from "lucide-react";
import {
  CASH_GAIN_ANIMATION_DURATION_SECONDS,
  CASH_LOSS_ANIMATION_DURATION_SECONDS,
  PLAYER_CHIP_COLORS,
} from "@/config";
import { useTheme } from "@/stores/ThemeContext";
import { Popover, PopoverContent, PopoverTrigger } from "../ui/popover";
import TelegramIcon from "../ui/icons/TelegramIcon";
import Separator from "./Separator";
import { useGameStore } from "@/stores/GameStore";
import { PopoverClose } from "@radix-ui/react-popover";
import { useTradeStore } from "@/stores/TradeStore";

type PlayerCardProps = {
  player: Player;
};

function PlayerCard({ player }: PlayerCardProps) {
  const { data: game } = useGame();
  const { me } = useGameStore();
  const { initTradeMenuData } = useTradeStore();
  const [isCurrentPlayer, setIsCurrentPlayer] = useState(false);
  const [primaryColor, _] = PLAYER_CHIP_COLORS[player.color as keyof typeof PLAYER_CHIP_COLORS];
  const [cashLoss, setCashLoss] = useState(0);
  const [cashGain, setCashGain] = useState(0);
  const [currentEffect, setCurrentEffect] = useState<GameEffect | null>(null);
  const [actionTimeout, setActionTimeout] = useState<number | null>(null);
  const [afkProgress, setAfkProgress] = useState(0);

  const { textColor, secondaryBGColor, bgColor, hintColor } = useTheme();

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
          console.log("CASH LOSS", previousPlayer.cash - player.cash);
          setCashLoss(previousPlayer.cash - player.cash);
        } else if (previousPlayer.cash < player.cash) {
          console.log("CASH GAIN", player.cash - previousPlayer.cash);
          setCashGain(player.cash - previousPlayer.cash);
        }
      }

      if (player.effects.length > 0) {
        setCurrentEffect(player.effects[0]);
      } else {
        setCurrentEffect(null);
      }
    }
  }, [game, player]);

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

  useEffect(() => {
    if (currentEffect) {
      let effectTimeout = player.effects[0].effect_data!.timeout;
      let unixTimestampInSeconds = Date.now();
      setActionTimeout(Math.floor((effectTimeout - unixTimestampInSeconds) / 1000));

      const interval = setInterval(() => {
        let unixTimestampInSeconds = Date.now();
        setActionTimeout(Math.floor((effectTimeout - unixTimestampInSeconds) / 1000));
      }, 1000);
      return () => clearInterval(interval);
    }
  }, [currentEffect]);

  useEffect(() => {
    if (currentEffect) {
      let effectTimeout = player.effects[0].effect_data!.timeout;
      let effectCreated = player.effects[0].effect_data!.created;
      let timeoutTime = effectTimeout - effectCreated;

      const interval = setInterval(() => {
        let unixTimestampInSeconds = Date.now();
        let timePassed = unixTimestampInSeconds - effectCreated;
        let circleProgress = (360 * timePassed) / timeoutTime;

        setAfkProgress(circleProgress);
      }, 1000 / 60);
      return () => clearInterval(interval);
    }
  }, [currentEffect]);

  useEffect(() => {
    if (!isCurrentPlayer) {
      setActionTimeout(null);
      setAfkProgress(0);
    }
  }, [isCurrentPlayer]);

  return (
    <Popover>
      <PopoverTrigger asChild>
        <Card className="relative">
          {player.status === PlayerStatus.TIMEOUT && (
            <div className="pointer-events-none absolute left-0 top-0 z-20 flex h-full w-full items-center justify-center rounded-xl">
              <Skull
                className="z-20"
                style={{
                  color: textColor,
                }}
              />
              <div
                className="absolute h-full w-full rounded-xl bg-black opacity-80"
                style={{
                  backgroundColor: secondaryBGColor,
                }}
              ></div>
            </div>
          )}
          <CardContent className="flex gap-2 p-2">
            <div className="relative">
              <div
                className="absolute aspect-square rounded-full"
                style={{
                  width: "calc(100% + 4px)",
                  // height: "calc(100% + 4px)",
                  top: "-2px",
                  left: "-2px",
                  background: `conic-gradient(${bgColor} ${afkProgress < 360 ? afkProgress : 0}deg, ${primaryColor} ${afkProgress < 360 ? afkProgress : 0}deg, ${primaryColor} 360deg)`,
                  transition: "background 0.5s ease",
                }}
              ></div>
              <Avatar
              // className="border-2"
              // style={{
              //   borderColor: primaryColor || "black",
              // }}
              >
                {/* Action timeout counter */}
                {actionTimeout !== null && (
                  <div className="absolute flex h-full w-full items-center justify-center">
                    <p
                      className="z-10"
                      style={{
                        color: textColor,
                      }}
                    >
                      {actionTimeout}
                    </p>
                    <div className="absolute h-full w-full bg-black opacity-50"></div>
                  </div>
                )}
                <AvatarImage src={player.avatar} />
                <AvatarFallback>o_o</AvatarFallback>
              </Avatar>
            </div>
            <div className="h-full w-full">
              <p className="text-sm">
                {player.name} {player.id} {player.status}
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
                  color: hintColor,
                }}
              >
                $ {player.cash}
              </p>
            </div>
          </CardContent>
          <div className="absolute right-0 top-0">{isCurrentPlayer && <Dices />}</div>
        </Card>
      </PopoverTrigger>
      <PopoverContent side="top" className="p-0 focus:outline-none">
        {me?.id === player.id ? (
          <div className="flex flex-col">
            <button className="flex h-1/4 w-full items-center justify-start gap-4 p-3">
              <FlagIcon />
              {"Surrender"}
            </button>
          </div>
        ) : (
          <div className="flex flex-col">
            <PopoverClose asChild>
              <button className="flex w-full items-center justify-start gap-4 p-3 focus:outline-none">
                <TelegramIcon className="h-5" />
                {"Send message"}
              </button>
            </PopoverClose>
            <Separator />
            <PopoverClose asChild>
              <button
                className="flex w-full items-center justify-start gap-4 p-3 focus:outline-none"
                onClick={() => {
                  initTradeMenuData(me!.id, player.id);
                }}
              >
                <HandshakeIcon />
                {"Trade"}
              </button>
            </PopoverClose>
          </div>
        )}
      </PopoverContent>
    </Popover>
  );
}

export default PlayerCard;
