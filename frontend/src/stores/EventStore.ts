import {
  Game,
  GameActionType,
  GameEffectType,
  GameEvent,
  GameEventType,
  GameFrame,
  GameScopeType,
  Ownership,
  Player,
} from "@/types/api";
import { create } from "zustand";

import { buildTradeMenuDataFromServerResponse, getMeFromPlayers, sleep } from "@/lib/utils";
import {
  COIN_FLIP_ANIMATION_DURATION_MS,
  COIN_FLIP_RESULT_DURATION_MS,
  DICE_ANIMATION_DURATION_SECONDS,
  PLAYER_CHIP_MOVE_DURATION_MS,
} from "@/config";
import { useGameStore } from "./GameStore";
import { queryClient } from "@/lib/queryClient";
import { useTradeStore } from "./TradeStore";

interface EventStore {
  eventQueue: GameEvent[] | [];
  eventLog: GameEvent[] | [];
  isProcessing: boolean;
  addEvents: (event: GameEvent[]) => void;
  addEventLog: (event: GameEvent[]) => void;
  processNextEvent: () => void;
  processGameFrame: (gameFrame: GameFrame) => void;
}

export const useEventStore = create<EventStore>((set, get) => ({
  eventQueue: [],
  eventLog: [],
  isProcessing: false,
  addEventLog: (events: GameEvent[]) => {
    set((state) => ({ eventLog: [...state.eventLog, ...events] }));
  },
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

      const { setPlayers, setGame, myTurn, setShowTurnMenu, setMe, setOwnerships } =
        useGameStore.getState();

      let players = queryClient.getQueryData<Player[]>(["players"]);
      if (!players) {
        return;
      }

      let game = queryClient.getQueriesData<Game>(["game"])[0][1];
      let ownerships = queryClient.getQueriesData<Ownership[]>(["ownerships"])[0][1];

      let me = getMeFromPlayers(players);
      if (!me) {
        console.error("No me found");
        return;
      }

      setMe(me);
      setPlayers(players);
      setGame(game);
      setOwnerships(ownerships);

      if (myTurn) {
        setShowTurnMenu(true);
      }
      return;
    }

    set({ isProcessing: true });
    const eventToProcess = eventQueue[0];

    try {
      await processEvent(eventToProcess);
    } finally {
      set((state) => ({
        eventLog: [...state.eventLog, eventToProcess],
        eventQueue: state.eventQueue.slice(1),
      }));
      // Continue processing next event
      get().processNextEvent();
    }
  },
  processGameFrame: (gameFrame: GameFrame) => {
    const { setShowTradeMenu, setTradeMenuData, setIsPreview } = useTradeStore.getState();
    if (gameFrame.type === GameScopeType.GAME_CONNECTED) {
      let players = queryClient.getQueryData<Player[]>(["players"]);
      if (!players) {
        return;
      }
      let me = getMeFromPlayers(players);
      let lastEffect = me?.effects[0];

      if (lastEffect) {
        if (lastEffect.name === GameEffectType.IN_TRADE) {
          setShowTradeMenu(true);
          setIsPreview(true);
          setTradeMenuData(buildTradeMenuDataFromServerResponse(lastEffect.effect_data));
        }
      }
    }
  },
}));

const processEvent = async (event: GameEvent) => {
  const { setDices, setShowDices, setShowTurnMenu, movePlayer, setCoinRotation, setWonCasino, me } =
    useGameStore.getState();
  const { setShowTradeMenu, resetTrade, setTradeMenuData, setIsPreview } = useTradeStore.getState();

  if (event.action === GameActionType.ROLL_DICE) {
    setShowTurnMenu(false);
    setShowDices(true);
    setDices(event.dices);
    await sleep(DICE_ANIMATION_DURATION_SECONDS * 1000);
  } else if (event.action === GameActionType.MOVE_PLAYER) {
    console.log("Processing move player");
    movePlayer(event.player!, event.position!);
    await sleep(PLAYER_CHIP_MOVE_DURATION_MS);
    setShowDices(false);
  } else if (event.action === GameActionType.WON_CASINO) {
    setCoinRotation(360 * 6);
    await sleep(COIN_FLIP_ANIMATION_DURATION_MS + COIN_FLIP_RESULT_DURATION_MS);
    setWonCasino(true);
  } else if (event.action === GameActionType.LOST_CASINO) {
    setCoinRotation(360 * 7);
    await sleep(COIN_FLIP_ANIMATION_DURATION_MS + COIN_FLIP_RESULT_DURATION_MS);
    setWonCasino(false);
  } else if (event.action === GameEventType.TIMEOUT) {
    setShowTradeMenu(false);
    resetTrade();
  } else if (event.action == GameEventType.CREATE_TRADE) {
    if (event.to_player === me?.id) {
      let players = queryClient.getQueriesData<Player[]>(["players"])[0][1];
      let me = getMeFromPlayers(players);

      let tradeMenuData = buildTradeMenuDataFromServerResponse(me!.effects[0]!.effect_data);

      setTradeMenuData(tradeMenuData);
      setShowTradeMenu(true);
      setIsPreview(true);
    } else {
      setShowTradeMenu(false);
      resetTrade();
    }
  } else if (
    event.action === GameEventType.REJECT_TRADE ||
    event.action === GameEventType.ACCEPT_TRADE
  ) {
    setShowTradeMenu(false);
    resetTrade();
  }
};
