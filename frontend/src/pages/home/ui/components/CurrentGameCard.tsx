import type { Game } from "@/entities/types";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";
import { navigateToGame } from "@/shared/utils";
import React from "react";

interface CurrentGameCardProps {
  game: Game;
}

export const CurrentGameCard: React.FC<CurrentGameCardProps> = ({ game }) => {
  return (
    <Card>
      Current game
      <Button
        onClick={() => {
          navigateToGame(game);
        }}
      >
        Return
      </Button>
    </Card>
  );
};
