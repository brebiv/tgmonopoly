import { Game } from "@/types/api";
import { useGameStore } from "@/stores/GameStore";
import PlayerCard from "./PlayerCard";
import { Card, CardContent, CardHeader } from "../ui/card";
import { Users } from "lucide-react";
import { useTheme } from "@/stores/ThemeContext";
import PlayerCardSkeleton from "./PlayerCardSkeleton";
import { useEffect, useState } from "react";
import { Button } from "../ui/button";
import TelegramIcon from "../ui/icons/TelegramIcon";
import { leaveGame } from "@/api";

function GameLobby({ game }: { game: Game }) {
  const players = useGameStore((state) => state.players);
  const { secondaryBGColor, textColor } = useTheme();
  const [dotMultiplier, setDotMultiplier] = useState(0);
  const { me } = useGameStore();

  useEffect(() => {
    setDotMultiplier(0);
    const interval = setInterval(() => {
      setDotMultiplier((prev) => {
        if (prev < 3) {
          return prev + 1;
        } else {
          return 0;
        }
      });
    }, 500);
    return () => clearInterval(interval);
  }, []);

  if (!players) {
    return null;
  }

  return (
    <div
      className="flex h-screen w-full flex-col items-center gap-2 bg-green-900 p-4"
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
                Waiting for players
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
            {players &&
              players.length > 0 &&
              players.map((player) => (
                <PlayerCard key={player.id} player={player} disablePopover={true} />
              ))}
            {Array.from({ length: game.max_players - players.length }).map((_, i) => (
              <PlayerCardSkeleton key={i} />
            ))}
          </div>
          <div className="flex w-full justify-between gap-4">
            {me?.permissions?.abort_game === true ? (
              <Button variant={"destructive"} className="text-md">
                Abort game
              </Button>
            ) : (
              <Button
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
            )}
            <Button variant={"default"} className="text-md flex-1 gap-2">
              <TelegramIcon className="h-5" />
              Invite a friend
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default GameLobby;
