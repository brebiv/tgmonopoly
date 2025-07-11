import type { Meta, StoryObj } from "@storybook/react-vite";
import { ActionSheet } from "@/pages/game/ui/game/ActionSheet";
import { WebSocketContextProvider } from "@/app/providers/WebSocketProvider";
import initial_game_frame from "@/test/mocks/initial_game_frame";
import { mockTelegram } from "@/test/mocks/mockTelegram";

const meta = {
  component: ActionSheet,
} satisfies Meta<typeof ActionSheet>;

export default meta;

const withTelegram = (Story: any) => {
  (window as any).Telegram = mockTelegram;
  return <Story />;
};

const withWebSocketContext = (Story: any) => {
  return (
    <WebSocketContextProvider gameUUID={initial_game_frame.game.uuid}>
      <Story />
    </WebSocketContextProvider>
  );
};

type Story = StoryObj<typeof ActionSheet>;

export const RollDice: Story = {
  args: {
    isOpen: true,
  },
  globals: {
    viewport: { value: "iphoneSE3", isRotated: false },
  },
  decorators: [withWebSocketContext, withTelegram],
};
