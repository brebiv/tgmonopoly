import { joinGame } from "@/shared/api";
import { Button } from "@/shared/ui/Button";
import { navigateToGame } from "@/shared/utils";
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
      onClick={async () => {
        const resp_data = await joinGame(gameUUID);
        navigateToGame(resp_data.game_uuid);
      }}
    >
      <p className="text-lg w-12 text-button-text">{text}</p>
    </Button>
  );
};
