import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import {} from "@/entities/gameStore";
import type { Player, Tile } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import { DollarSignIcon } from "lucide-react";

interface BuyButtonProps {
  propertyTile: Tile;
  myPlayer: Player;
  protocol?: "ws" | "http";
}

export const BuyButton = ({ protocol = "ws" }: BuyButtonProps) => {
  const { send } = useWebSocketContext();

  const handleClickWS = () => {
    const command = "accept";
    send(command);
  };
  const handleClickHTTP = () => {
    console.error("Not implemented");
  };

  return (
    <Button
      className="flex gap-2 py-3 text-lg font-semibold"
      onClick={protocol == "ws" ? handleClickWS : handleClickHTTP}
    >
      <DollarSignIcon /> {"Buy"}
    </Button>
  );
};
