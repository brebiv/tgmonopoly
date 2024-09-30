import { GameActionType, GameEvent } from "@/types/api";
import { create } from "zustand";

import { queryClient } from "@/lib/queryClient";

interface EventStore {
  eventQueue: GameEvent[];
  isProcessing: boolean;
  addEvent: (event: GameEvent) => void;
  processNextEvent: () => void;
}

export const useEventStore = create<EventStore>((set, get) => ({
  eventQueue: [],
  isProcessing: false,

  addEvent: (event) => {
    set((state) => ({ eventQueue: [...state.eventQueue, event] }));
    // Start processing if not already
    if (!get().isProcessing) {
      get().processNextEvent();
    }
  },

  processNextEvent: async () => {
    const { eventQueue } = get();
    if (eventQueue.length === 0) {
      set({ isProcessing: false });
      console.log("No more events to process");
      return;
    }

    set({ isProcessing: true });
    const eventToProcess = eventQueue[0];

    try {
      await processEvent(eventToProcess);
    } finally {
      set((state) => ({
        eventQueue: state.eventQueue.slice(1),
      }));
      // Continue processing next event
      get().processNextEvent();
    }
  },
}));

const processEvent = async (event: GameEvent) => {
  if (event.action === GameActionType.START_GAME) {
    console.log("Processing start game");
    queryClient.setQueryData(["players"], () => event.players);
    queryClient.setQueryData(["game"], () => event.game);
  }
};
