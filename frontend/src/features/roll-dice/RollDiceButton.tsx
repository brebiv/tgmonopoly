// @ts-nocheck
import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { Button } from "@/shared/ui/Button";
import { DicesIcon } from "lucide-react";

interface RollDiceButtonProps {
  disabled?: boolean;
  protocol?: "ws" | "http";
}

export const RollDiceButton = ({ disabled = false, protocol = "ws" }: RollDiceButtonProps) => {
  const { send, sendJSON } = useWebSocketContext();

  const handleClickWS = () => {
    const command = { action: "roll_dice" };
    sendJSON(command);
  };
  const handleClickHTTP = () => {
    console.error("Not implemented");
  };

  return (
    <Button
      disabled={disabled}
      className="flex gap-2 py-3 text-lg font-semibold"
      onClick={protocol == "ws" ? handleClickWS : handleClickHTTP}
    >
      <DicesIcon /> {"Roll dice"}
    </Button>
  );
};
