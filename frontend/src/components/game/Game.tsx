import { useEffect, useState } from "react";
import Board from "./Board";

import { useAuth, useReactQuerySubscription } from "@/hooks";
import PlayersChipController from "./PlayersChipController";
import Forbidden from "../Forbidden";
import LoadingScreen from "../LoadingScreen";
import { Button } from "../ui/button";
import DiceController from "./DiceController";
import { sendGameAction } from "@/api";
import { GameActionType, GameStatus } from "@/types/api";
import { useEventStore } from "@/stores/EventStore";
import { useGameStore } from "@/stores/GameStore";
import PlayersSection from "./PlayersSection";
import TurnMenu from "./TurnMenu";

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
  const { data: auth, isLoading: isMeLoading, isError: isMeError } = useAuth(true);
  // const { data: game } = useGame();
  // const { data: players = [] } = usePlayers();
  const eventQueue = useEventStore((state) => state.eventQueue);

  const [boardLoaded, setBoardLoaded] = useState(false);
  const { me, myTurn, game, players } = useGameStore((state) => state);

  if (isMeError) {
    return <Forbidden />;
  }

  useReactQuerySubscription(gameUUID);

  useEffect(() => {
    console.log("Me", me);
  }, [me]);

  useEffect(() => {
    console.log("MyTurn", myTurn);
  }, [myTurn]);

  useEffect(() => {
    console.log("GameEventQueue", eventQueue);
  }, [eventQueue]);

  // useEffect(() => {

  // })

  useEffect(() => {
    if (game) {
      console.log("Game", game);
    }
    if (players) {
      console.log("Players", players);
    }
  }, [game, players]);

  if (game?.status === GameStatus.WAITING) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-green-900">
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

  return (
    <div
      className="flex min-h-screen flex-col gap-4"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.secondary_bg_color || "#334155",
      }}
    >
      {(auth == undefined ||
        isMeLoading ||
        game == undefined ||
        players == undefined ||
        !boardLoaded) && <LoadingScreen />}
      <PlayersChipController players={players} boardLoaded={boardLoaded} />
      <DiceController />
      <Board boardLoaded={boardLoaded} setBoardLoaded={setBoardLoaded} />
      <PlayersSection />
      <TurnMenu />
      {/* <Button
        style={{
          backgroundColor:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.button_color || "black",
          color:
            // @ts-ignore
            window.Telegram.WebApp.themeParams.button_text_color || "white",
        }}
        onClick={() => {
          // @ts-ignore
          queryClient.setQueryData(["players"], (oldData) => {
            // @ts-ignore
            const updatedPlayers = oldData.map((player, index) => {
              if (index === 0) {
                return { ...player, position: (player.position + 1) % 40 };
              }
              return player;
            });

            return updatedPlayers;
          });
        }}
      >
        Position + 1
      </Button> */}
    </div>
  );
}

export default Game;
