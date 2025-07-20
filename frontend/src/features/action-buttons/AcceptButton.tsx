import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import type { GameActionExtraData } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import type React from "react";

interface AcceptButtonProps {
  disabled?: boolean;
  extraDataFunc?: () => GameActionExtraData;
  protocol?: "ws" | "http";
  onClick?: () => void;
  children: React.ReactNode;
}

export const AcceptButton: React.FC<AcceptButtonProps> = ({
  disabled,
  extraDataFunc,
  protocol = "ws",
  onClick,
  children,
}) => {
  const { sendJSON } = useWebSocketContext();

  const handleClickWS = () => {
    const command = { action: "accept" };
    if (extraDataFunc) {
      Object.assign(command, extraDataFunc());
    }
    sendJSON(command);
  };
  const handleClickHTTP = () => {
    console.error("Not implemented");
  };

  return (
    <Button
      disabled={disabled}
      className="flex gap-2 py-3 text-lg font-semibold"
      onClick={onClick ? onClick : protocol == "ws" ? handleClickWS : handleClickHTTP}
    >
      {children}
    </Button>
  );
};
