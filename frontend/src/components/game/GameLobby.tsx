import { Game, GameStatus, Player } from "@/types/api";
import { useGameStore } from "@/stores/GameStore";
import PlayerCard from "./PlayerCard";
import { Card, CardContent, CardHeader } from "../ui/card";
import { Users } from "lucide-react";
import { useTheme } from "@/stores/ThemeContext";
import PlayerCardSkeleton from "./PlayerCardSkeleton";
import React, { useEffect, useState } from "react";
import { Button } from "../ui/button";
import TelegramIcon from "../ui/icons/TelegramIcon";
import { leaveGame } from "@/api";
import { cn } from "@/lib/utils";

function GameLobby({
  children,
  game,
  players,
  className = "",
}: {
  children?: React.ReactNode;
  game: Game;
  players?: Player[];
  className?: string;
}) {
  const gamePlayers = useGameStore((state) => state.players);
  const finalPlayers = players || gamePlayers;
  const { secondaryBGColor, textColor } = useTheme();
  const [dotMultiplier, setDotMultiplier] = useState(0);

  let gameStatusText: string | undefined = undefined;
  let animateDots = false;

  if (game.status === GameStatus.WAITING) {
    gameStatusText = "Waiting for players";
    animateDots = true;
  } else if (game.status === GameStatus.PLAYING) {
    gameStatusText = "Game is running!";
  } else if (game.status === GameStatus.FINISHED) {
    gameStatusText = "Game is finished";
  }

  useEffect(() => {
    let interval: NodeJS.Timeout | undefined;
    if (animateDots) {
      setDotMultiplier(0);
      interval = setInterval(() => {
        setDotMultiplier((prev) => {
          if (prev < 3) {
            return prev + 1;
          } else {
            return 0;
          }
        });
      }, 500);
      return () => clearInterval(interval);
    } else {
      setDotMultiplier(0);
      if (interval) {
        clearInterval(interval);
      }
    }
  }, []);

  if (!finalPlayers) {
    return null;
  }

  return (
    <div
      className={cn("flex h-screen w-full flex-col items-center gap-2 bg-green-900 p-4", className)}
      style={{
        backgroundColor: secondaryBGColor,
        color: textColor,
      }}
    >
      <Card className="w-full">
        <CardHeader>
          <div className="flex gap-2">
            <Users />
            Players
            <div className="relative ml-auto flex">
              <p className="h-full">
                {gameStatusText}
                {Array.from({ length: 3 }).map((_, i) => (
                  <span key={i} className={dotMultiplier > i ? "" : "invisible"}>
                    .
                  </span>
                ))}
              </p>
            </div>
          </div>
        </CardHeader>
        <CardContent className="flex flex-col gap-16">
          <div className="flex flex-col gap-2">
            {finalPlayers &&
              finalPlayers.length > 0 &&
              finalPlayers.map((player) => (
                <PlayerCard key={player.id} player={player} disablePopover={true} />
              ))}
            {Array.from({ length: game.max_players - finalPlayers.length }).map((_, i) => (
              <PlayerCardSkeleton key={i} />
            ))}
          </div>
          <div className="flex w-full justify-between gap-4">
            {children}
            {/* <Button
              variant={"destructive"}
              className="text-md"
              onClick={async () => {
                let resp = await leaveGame(game.uuid);
                if (resp.status === "ok") {
                  window.location.href = "/";
                }
              }}
            >
              Leave game
            </Button>
            <Button variant={"default"} className="text-md flex-1 gap-2">
              <TelegramIcon className="h-5" />
              Invite a friend
            </Button> */}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

GameLobby.Actions = ({
  children,
  game,
  className = "",
}: {
  children?: React.ReactNode;
  game: Game;
  className?: string;
}) => {
  if (React.Children.count(children) > 0) {
    return <div className={cn("flex w-full justify-between gap-4", className)}>{children}</div>;
  }

  const handleLeaveGame = async () => {
    let resp = await leaveGame(game.uuid);
    if (resp.status === "ok") {
      window.location.href = "/";
    }
  };

  return (
    <div className={`flex w-full justify-between gap-4 ${className}`}>
      <Button variant={"destructive"} className="text-md" onClick={handleLeaveGame}>
        Leave game
      </Button>
      <Button variant="default" className="text-md flex-1 gap-2">
        <TelegramIcon className="h-5" />
        Invite a friend
      </Button>
    </div>
  );
};

export default GameLobby;
