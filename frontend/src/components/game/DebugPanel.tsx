import { useEffect } from "react";
import ThemedDiv from "../ui/ThemedDiv";
import { useAuth, useGame, useOwnerships, usePlayers } from "@/hooks";
import { useGameStore } from "@/stores/GameStore";
import { useEventStore } from "@/stores/EventStore";

function DebugPanel() {
  const { me, myTurn } = useGameStore((state) => state);
  const { data: game } = useGame();
  const { data: players = [] } = usePlayers();
  const { data: ownerships } = useOwnerships();

  const eventQueue = useEventStore((state) => state.eventQueue);
  // @ts-ignore
  const gameUUID = window.location.pathname.split("/")[2];
  // @ts-ignore
  const { data: auth, isLoading: isMeLoading, isError: isMeError } = useAuth(true);

  useEffect(() => {
    if (game) {
      console.log("Game", game);
    }
    if (players) {
      console.log("Players", players);
    }
  }, [game, players]);

  useEffect(() => {
    console.log("ownerships", ownerships);
  }, [ownerships]);

  useEffect(() => {
    console.log("Me", me);
  }, [me]);

  useEffect(() => {
    console.log("MyTurn", myTurn);
  }, [myTurn]);

  useEffect(() => {
    console.log("GameEventQueue", eventQueue);
  }, [eventQueue]);

  return (
    <ThemedDiv className="absolute flex h-full w-full flex-col items-center p-1">
      <h1>⚙️ My little debug panel</h1>
      <p>Game turn: {game?.turn}</p>
    </ThemedDiv>
  );
}

export default DebugPanel;
