import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { Button } from "@/shared/ui/Button";
import type React from "react";

interface AcceptActionButtonProps {
  protocol?: "ws" | "http";
  children: React.ReactNode;
}

export const AcceptActionButton: React.FC<AcceptActionButtonProps> = ({ protocol = "ws", children }) => {
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
      {children}
    </Button>
  );
};
