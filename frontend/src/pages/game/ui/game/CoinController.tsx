import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { useGameStore } from "@/entities/gameStore";
import Coin from "@/shared/ui/Coin";

export const CoinController = () => {
  const isCasinoBet = useGameStore((s) => s.isCasinoBet);
  const flipCoin = useGameStore((s) => s.flipCoin);
  const { sendJSON } = useWebSocketContext();

  return (
    <Coin
      disabled={!isCasinoBet}
      rotation={flipCoin ? 360 * 6 : 0}
      onClick={() => {
        const command = { action: "accept" };
        sendJSON(command);
      }}
    />
  );
};
