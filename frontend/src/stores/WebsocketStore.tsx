import { create } from "zustand";

interface WebsocketStore {
  connected: boolean | undefined;
  setConnected: (connected: boolean) => void;
}

export const useWebsocketStore = create<WebsocketStore>((set) => ({
  connected: undefined,
  setConnected: (connected: boolean) => {
    set({ connected });
  },
}));
