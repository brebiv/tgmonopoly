import type { Preview } from "@storybook/react-vite";
import { INITIAL_VIEWPORTS } from "storybook/viewport";
import { initialize, mswLoader } from "msw-storybook-addon";
import { QueryClientProvider } from "@tanstack/react-query";
import { withThemeByClassName } from "@storybook/addon-themes";

import { queryClient } from "../src/shared/queryClient";
import { handlers } from "../src/test/mocks/handlers.ts";
import "../src/stories/assets/style/tailwind.css";

initialize(undefined, handlers);

const withQueryClient = (Story: any) => {
  return (
    <QueryClientProvider client={queryClient}>
      <Story />
    </QueryClientProvider>
  );
};

const preview: Preview = {
  parameters: {
    controls: {
      matchers: {
        color: /(background|color)$/i,
        date: /Date$/i,
      },
    },
    viewport: {
      options: INITIAL_VIEWPORTS,
    },
    layout: "fullscreen",
  },
  loaders: [mswLoader],
  decorators: [
    withQueryClient,
    withThemeByClassName({
      themes: {
        light: "light",
        dark: "dark",
      },
      defaultTheme: "light",
    }),
  ],
};

export default preview;
