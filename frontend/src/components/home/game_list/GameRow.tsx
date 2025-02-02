import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { useTheme } from "@/stores/ThemeContext";
import { Game } from "@/types/api";
import { Button } from "@/components/ui/button";
import Separator from "@/components/game/Separator";

function GameRow({ game }: { game: Game }) {
  const { hintColor } = useTheme();

  return (
    <Card className="flex min-h-20 w-full flex-1 flex-col gap-3 px-4 py-2">
      <div className="flex w-full gap-3">
        <div className="flex w-3/4 gap-3 overflow-hidden">
          {/* <AvatarGroup> */}
          {game.players.map((player) => (
            <div key={player.id} className="flex flex-col items-center">
              <Avatar>
                {/* <AvatarImage src={player.avatar} /> */}
                <AvatarFallback>o_o</AvatarFallback>
              </Avatar>
              {/* <p>Player1</p> */}
              {/* <p className="text-sm font-thin" style={{ color: hintColor }}>
                    14
                  </p> */}
            </div>
          ))}
          {Array.from({ length: game.max_players - game.players.length }).map((_, i) => (
            <div key={i} className="flex flex-col items-center">
              <Avatar>
                <AvatarFallback
                  className="border-2 border-dashed"
                  style={{ backgroundColor: "transparent", borderColor: hintColor }}
                ></AvatarFallback>
              </Avatar>
            </div>
          ))}
          {/* </AvatarGroup> */}
        </div>
        <div className="flex w-1/4 items-center">
          <Button variant={"default"} className="w-full font-semibold">
            Join
          </Button>
        </div>
      </div>
      <Separator className="mt-2" style={{ backgroundColor: "rgb(100,100,100)" }} />
    </Card>
  );
}

export default GameRow;
