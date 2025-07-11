import type { Meta, StoryObj } from "@storybook/react-vite";
import { WebSocketContextProvider } from "@/app/providers/WebSocketProvider";
import initial_game_frame from "@/test/mocks/initial_game_frame";
import { mockTelegram } from "@/test/mocks/mockTelegram";
import { Game } from "@/pages/game/ui/game/Game";
import { mockGameStore } from "@/test/mocks/utils";
import { GameFrameTypes, type GameFrame } from "@/entities/types";
import { useGameStore } from "@/entities/gameStore";

const meta = {
  title: "Game Actions/RollDice",
  component: Game,
} satisfies Meta<typeof Game>;

export default meta;

const withTelegram = (Story: any) => {
  (window as any).Telegram = mockTelegram;
  return <Story />;
};
const withGameStore = (Story: any) => {
  mockGameStore();
  return <Story />;
};

const withWebSocketContext = (Story: any) => {
  const { processInitialGameFrame, processEventGameFrame } = useGameStore();
  const handleMessage = (message: any) => {
    console.log("Handling message");

    let data: GameFrame = JSON.parse(message);

    console.log(data);

    if (data.type === GameFrameTypes.GAME_INITIAL) {
      processInitialGameFrame(data);
    } else if (data.type === GameFrameTypes.GAME_EVENT) {
      processEventGameFrame(data);
    }
  };

  return (
    <WebSocketContextProvider gameUUID={initial_game_frame.game.uuid} onMessage={handleMessage}>
      <Story />
    </WebSocketContextProvider>
  );
};

type Story = StoryObj<typeof Game>;

export const RollDice: Story = {
  args: {},
  globals: {
    viewport: { value: "iphoneSE3", isRotated: false },
  },
  decorators: [withWebSocketContext, withTelegram, withGameStore],
};
