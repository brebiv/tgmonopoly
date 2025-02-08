import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Card } from "@/components/ui/card";
import { useTheme } from "@/stores/ThemeContext";
import { Game } from "@/types/api";
import { Button } from "@/components/ui/button";
import Separator from "@/components/game/Separator";
import { joinGame } from "@/api";

function GameListRow({
  game,
  hideSeparator = false,
  reconnect = false,
}: {
  game: Game;
  hideSeparator?: boolean;
  reconnect?: boolean;
}) {
  const { hintColor } = useTheme();

  return (
    <Card className="flex h-auto w-full flex-col gap-3 px-4 py-4">
      <div className="flex w-full gap-3">
        <div className="flex w-3/4 gap-3 overflow-hidden">
          {/* <AvatarGroup> */}
          {game.players.map((player) => (
            <div key={player.id} className="flex flex-col items-center gap-1">
              <Avatar>
                {/* <AvatarImage src={player.avatar} /> */}
                <AvatarFallback>{player.name.charAt(0).toUpperCase()}</AvatarFallback>
              </Avatar>
              <p className="text-sm">{player.name}</p>
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
          {game.in_game || reconnect ? (
            <Button
              variant={"default"}
              className="w-full font-semibold"
              onClick={() => {
                window.location.href = "/game/" + game.uuid;
              }}
            >
              Reconnect
            </Button>
          ) : (
            <Button
              variant={"default"}
              className="w-full font-semibold"
              onClick={async () => {
                let resp = await joinGame(game.uuid);
                if (resp.status === "ok") {
                  window.location.href = resp.next_url;
                }
              }}
            >
              Join
            </Button>
          )}
        </div>
      </div>
      {!hideSeparator && (
        <Separator className="mt-2" style={{ backgroundColor: "rgb(100,100,100)" }} />
      )}
      {/* <Separator className="mt-2" style={{ backgroundColor: "rgb(100,100,100)" }} /> */}
    </Card>
  );
}

export default GameListRow;
