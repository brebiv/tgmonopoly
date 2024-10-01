import { Game, GameActionType, GameEvent, Player } from "@/types/api";
import { create } from "zustand";

import { sleep } from "@/lib/utils";
import { DICE_ANIMATION_DURATION_SECONDS, PLAYER_CHIP_MOVE_DURATION_MS } from "@/config";
import { useGameStore } from "./GameStore";
import { queryClient } from "@/lib/queryClient";

interface EventStore {
  eventQueue: GameEvent[] | [];
  isProcessing: boolean;
  addEvents: (event: GameEvent[]) => void;
  processNextEvent: () => void;
}

export const useEventStore = create<EventStore>((set, get) => ({
  eventQueue: [],
  isProcessing: false,

  addEvents: (events: GameEvent[]) => {
    set((state) => ({ eventQueue: [...state.eventQueue, ...events] }));
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

      const { setPlayers, setGame } = useGameStore.getState();
      let players = queryClient.getQueriesData<Player[]>(["players"])[0][1];
      let game = queryClient.getQueriesData<Game>(["game"])[0][1];

      setPlayers(players);
      setGame(game);
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
  const { setDices, setShowDices, setShowTurnMenu, movePlayer } = useGameStore.getState();

  if (event.action === GameActionType.START_GAME) {
    console.log("Processing start game");
  } else if (event.action === GameActionType.ROLL_DICE) {
    console.log("Processing roll dice");

    setShowTurnMenu(false);
    setShowDices(true);
    setDices(event.dices);
    await sleep(DICE_ANIMATION_DURATION_SECONDS * 1000);
  } else if (event.action === GameActionType.MOVE_PLAYER) {
    console.log("Processing move player");
    movePlayer(event.player!, event.position!);
    await sleep(PLAYER_CHIP_MOVE_DURATION_MS);
    setShowDices(false);
  }
};
