import { leaveGame } from "@/shared/api";
import { Button } from "@/shared/ui/Button";
import { navigateTo } from "@/shared/utils";
import type React from "react";

interface LeaveGameButtonProps {
  gameUUID: string;
  children?: React.ReactNode;
}

export const LeaveGameButton: React.FC<LeaveGameButtonProps> = ({
  gameUUID,
  children,
}) => {
  return (
    <Button
      onClick={() => {
        leaveGame(gameUUID);
        navigateTo("/");
      }}
      className="w-full"
    >
      {children ? children : <>Leave game</>}
    </Button>
  );
};
