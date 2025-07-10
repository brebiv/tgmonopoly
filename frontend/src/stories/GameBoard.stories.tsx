import type { Meta, StoryObj } from "@storybook/react-vite";
import { GameBoard } from "@/pages/game/ui/game/GameBoard";
import classic_board_config from "@/test/mocks/classic_board_config";

import { useState } from "react";
import { Button } from "@/shared/ui/Button";
import { generateRandomPlayers } from "@/test/mocks/utils";

const playerPresets = {
  TwoPlayers: [...generateRandomPlayers(2)],
  FourPlayers: [...generateRandomPlayers(4)],
};

const meta = {
  component: GameBoard,
  decorators: [(Story) => <div className="relative h-full">{Story()}</div>],
  argTypes: {
    players: {
      options: Object.keys(playerPresets),
      mapping: playerPresets,
      control: "select",
    },
  },
} satisfies Meta<typeof GameBoard>;

export default meta;

type Story = StoryObj<typeof GameBoard>;

export const Classic: Story = {
  args: {
    // @ts-ignore
    players: "TwoPlayers",
    boardConfig: classic_board_config,
  },
  globals: {
    viewport: { value: "iphoneSE3", isRotated: false },
  },
  render: (args) => {
    const [players, setPlayers] = useState(args.players);

    const bumpPos = (id: number) =>
      setPlayers((prev) => prev.map((p) => (p.id === id ? { ...p, position: p.position + 1 } : p)));

    return (
      <div className="bg-secondary-background h-screen w-full overflow-hidden">
        <GameBoard {...args} players={players}>
          {/* For debugging */}
          <div className="flex w-full justify-center pt-2">
            <Button onClick={() => bumpPos(1)}>position +1</Button>
          </div>
        </GameBoard>
      </div>
    );
  },
};
