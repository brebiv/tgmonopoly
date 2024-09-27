import { useEffect, useState } from "react";
import Board from "./Board";

import { useGame, useMe, usePlayers, useReactQuerySubscription } from "@/hooks";
import PlayersChipController from "./PlayersChipController";
import Forbidden from "../Forbidden";
import LoadingScreen from "../LoadingScreen";
import { Button } from "../ui/button";
import { useQueryClient } from "react-query";

function Game() {
  useEffect(() => {
    // @ts-ignore
    // window.Telegram.WebApp.BackButton.hide();
    window.Telegram.WebApp.BackButton.show();
    // @ts-ignore
    window.Telegram.WebApp.BackButton.onClick(() => {
      window.location.href = "/";
      // @ts-ignore
      window.Telegram.WebApp.BackButton.hide();
      return true;
    });
  }, []);

  const gameUUID = window.location.pathname.split("/")[2];
  const { data: me, isLoading: isMeLoading, isError: isMeError } = useMe(true);
  const { data: game } = useGame();
  const { data: players = [] } = usePlayers();

  const [boardLoaded, setBoardLoaded] = useState(false);

  if (isMeError) {
    return <Forbidden />;
  }

  useReactQuerySubscription(gameUUID);

  useEffect(() => {
    if (game) {
      console.log("Game", game);
    }
    if (players) {
      console.log("Players", players);
    }
  }, [game, players]);

  const queryClient = useQueryClient();

  return (
    <div
      className="flex min-h-screen flex-col"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.bg_color || "#334155",
      }}
    >
      {(me == undefined ||
        isMeLoading ||
        game == undefined ||
        players == undefined ||
        !boardLoaded) && <LoadingScreen />}
      <Board boardLoaded={boardLoaded} setBoardLoaded={setBoardLoaded} />
      <PlayersChipController players={players} boardLoaded={boardLoaded} />
      <div className="flex flex-col items-center pt-4">
        <Button
          onClick={() => {
            // @ts-ignore
            queryClient.setQueryData(["players"], (oldData) => {
              // @ts-ignore
              const updatedPlayers = oldData.map((player, index) => {
                if (index === 0) {
                  return { ...player, position: (player.position + 10) % 40 };
                }
                return player;
              });

              // Return the updated players data
              console.log({ updatedPlayers });

              return updatedPlayers;
            });
          }}
        >
          Position + 1
        </Button>
      </div>
    </div>
  );
}

export default Game;
