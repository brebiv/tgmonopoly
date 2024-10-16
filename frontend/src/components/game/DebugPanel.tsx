import ThemedDiv from "../ui/ThemedDiv";
import { useGame } from "@/hooks";

function DebugPanel() {
  //   const { me } = useGameStore((state) => state);
  const { data: game } = useGame();
  //   const { data: players = [] } = usePlayers();
  //   const gameUUID = window.location.pathname.split("/")[2];
  //   const { data: auth, isLoading: isMeLoading, isError: isMeError } = useAuth(true);

  return (
    <ThemedDiv className="absolute flex h-full w-full flex-col items-center p-1">
      <h1>⚙️ My little debug panel</h1>
      <p>Game turn: {game?.turn}</p>
    </ThemedDiv>
  );
}

export default DebugPanel;
