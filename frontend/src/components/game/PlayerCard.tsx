import { Player } from "@/types/api";
import { Avatar, AvatarFallback, AvatarImage } from "../ui/avatar";
import { Card, CardContent } from "../ui/card";
import { useEffect, useState } from "react";
import { useGame } from "@/hooks";
import { Dices } from "lucide-react";

type PlayerCardProps = {
  player: Player;
};

function PlayerCard({ player }: PlayerCardProps) {
  const { data: game } = useGame();
  const [isCurrentPlayer, setIsCurrentPlayer] = useState(false);

  useEffect(() => {
    if (game) {
      if (game.current_player == player.id) {
        setIsCurrentPlayer(true);
      } else {
        setIsCurrentPlayer(false);
      }
    }
  }, [game]);

  return (
    <Card className="relative">
      <CardContent className="flex gap-2 p-2">
        <Avatar
          className="border-2"
          style={{
            borderColor: player.color || "unset",
          }}
        >
          <AvatarImage src={player.avatar} />
          <AvatarFallback>o_o</AvatarFallback>
        </Avatar>
        <div className="h-full w-full">
          <p className="text-sm">
            {player.name} {player.id}
          </p>
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
