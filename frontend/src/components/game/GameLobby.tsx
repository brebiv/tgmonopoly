import { sendGameAction } from "@/api";
import { Button } from "../ui/button";
import { GameActionType } from "@/types/api";
import { useGameStore } from "@/stores/GameStore";
import PlayerCard from "./PlayerCard";
import { Card, CardContent, CardHeader } from "../ui/card";
import { Users } from "lucide-react";

function GameLobby() {
  const gameUUID = window.location.pathname.split("/")[2];
  const players = useGameStore((state) => state.players);

  return (
    <div
      className="flex h-screen w-full flex-col items-center bg-green-900 p-4"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.secondary_bg_color || "#334155",
        color:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.text_color || "white",
      }}
    >
      <Card className="w-full">
        <CardHeader>
          <div className="flex gap-2">
            <Users />
            Players
          </div>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-2">
            {players &&
              players.length > 0 &&
              players.map((player) => <PlayerCard key={player.id} player={player} />)}
          </div>
        </CardContent>
      </Card>
      <Button
        style={{
          backgroundColor:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.button_color || "black",
          color:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.button_text_color || "white",
        }}
        onClick={() => {
          sendGameAction({ action: GameActionType.START_GAME, game_uuid: gameUUID });
        }}
      >
        Start game
      </Button>
    </div>
  );
}

export default GameLobby;
