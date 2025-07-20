import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { GameActionType, type GameActionExtraData } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import type React from "react";

interface RejectButtonProps {
  action?: GameActionType;
  extra_data?: GameActionExtraData;
  protocol?: "ws" | "http";
  children: React.ReactNode;
}

export const RejectButton: React.FC<RejectButtonProps> = ({
  action,
  extra_data,
  protocol = "ws",
  children,
}) => {
  const { sendJSON } = useWebSocketContext();

  const handleClickWS = () => {
    const command = { action: action || GameActionType.REJECT, ...extra_data };
    sendJSON(command);
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
