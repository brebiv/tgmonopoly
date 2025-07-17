import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { GameActionType } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import type React from "react";

interface RejectButtonProps {
  action?: GameActionType;
  protocol?: "ws" | "http";
  children: React.ReactNode;
}

export const RejectButton: React.FC<RejectButtonProps> = ({ action, protocol = "ws", children }) => {
  const { send } = useWebSocketContext();

  const handleClickWS = () => {
    const command = action || GameActionType.REJECT;
    send(command);
  };
  const handleClickHTTP = () => {
    console.error("Not implemented");
  };

  return (
    <Button
      className="bg-destructive flex gap-2 py-3 text-lg font-semibold"
      onClick={protocol == "ws" ? handleClickWS : handleClickHTTP}
    >
      {children}
    </Button>
  );
};
