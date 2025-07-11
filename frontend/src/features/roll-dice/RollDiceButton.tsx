import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { Button } from "@/shared/ui/Button";
import { DicesIcon } from "lucide-react";

interface RollDiceButtonProps {
  protocol?: "ws" | "http";
}

export const RollDiceButton = ({ protocol = "ws" }: RollDiceButtonProps) => {
  const { send } = useWebSocketContext();

  const handleClickWS = () => {
    const command = "roll_dice";
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
      <DicesIcon /> {"Roll dice"}
    </Button>
  );
};
