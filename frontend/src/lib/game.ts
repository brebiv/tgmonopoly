import { useGameStore } from "@/stores/GameStore";
import { Game } from "@/types/api";

export const processGameData = (gameData: Game) => {
  const me = useGameStore.getState().me;
  const setMyTurn = useGameStore.getState().setMyTurn;

  if (!me) {
    return;
  }

  if (gameData.current_player == me.id) {
    console.log("Setting my turn to true");
    setMyTurn(true);
  } else {
    console.log("Setting my turn to false");
    setMyTurn(false);
  }
};
