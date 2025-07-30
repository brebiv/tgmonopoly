import type { Game } from "@/entities/types";
import { Avatar } from "@/shared/ui/Avatar";
import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";
import { navigateToGame } from "@/shared/utils";
import React from "react";

interface CurrentGameCardProps {
  game: Game;
}

export const CurrentGameCard: React.FC<CurrentGameCardProps> = ({ game }) => {
  return (
    <Card className="h-full w-full">
      <h1>Current game</h1>
      <div className="flex">
        <div
          className="grid h-12 gap-2"
          style={{
            gridTemplateColumns: `repeat(${game.max_players}, minmax(0, 1fr))`,
          }}
        >
          {Array.from({ length: game.max_players }).map((_, i) => {
            return game.players[i] ? (
              <div key={i} className="h-12">
                <Avatar player={game.players[i]} />
              </div>
            ) : (
              <div className="h-12">
                <Avatar key={i} />
              </div>
            );
          })}
        </div>
      </div>
      <Button
        onClick={() => {
          navigateToGame(game.uuid);
        }}
      >
        <p className="text-button-text w-12 text-lg">{"Return"}</p>
      </Button>
    </Card>
  );
};
