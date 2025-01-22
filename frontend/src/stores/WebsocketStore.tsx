import { create } from "zustand";

interface WebsocketStore {
  connected: boolean | undefined;
  setConnected: (connected: boolean) => void;
}

// @ts-ignore
export const useWebsocketStore = create<WebsocketStore>((set, get) => ({
  connected: false,
  setConnected: (connected: boolean) => {
    set({ connected });
  },
}));
