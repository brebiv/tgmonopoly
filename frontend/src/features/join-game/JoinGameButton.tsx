import { Button } from "@/shared/ui/Button";
import type React from "react";

interface JoinGameButtonProps {
  gameUUID: string;
  text?: string;
}

export const JoinGameButton: React.FC<JoinGameButtonProps> = ({
  gameUUID,
  text = "Join",
}) => {
  return (
    <Button
      onClick={() => {
        console.log("Joining game:", gameUUID);
      }}
    >
      <p className="text-lg w-12 text-button-text">{text}</p>
    </Button>
  );
};
