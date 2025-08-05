import { sleep } from "@/shared/utils";
import { create } from "zustand";

export type MenuTabs = "games" | "friends" | "store" | "create_game";
export type DayStatuses = "past" | "present" | "future";
export type StreakDay = {
  day: number;
  status: DayStatuses;
  reward: number;
  claimed: boolean;
};
export type HomeData = {
  streak: StreakDay[];
  coins: number;
};

export enum DailyRewardAnimationState {
  AWAIT = 0,
  CARD_SHAKING = 1,
  COINS_BOOM = 2,
  FINISHED = 3,
}

type HomeStore = {
  menuTab: MenuTabs;
  setMenuTab: (value: MenuTabs) => void;
  homeData?: HomeData;
  initHomeData: (value: HomeData) => void;

  coins: number;
  setCoins: (value: number) => void;
  addCoins: (value: number) => void;

  // Daily reward
  coinsCount: number;
  streak: StreakDay[];
  coinsFinishCount: number;
  amountPerCoin: number;
  fireCoins: boolean;
  setFireCoins: (value: boolean) => void;
  fireShaking: boolean;
  incCoinsFinishCount: () => void;
  resetCoinsFinishCount: () => void;
  handleCoinFinished: () => void;
  claimCurrentDay: () => void;
  inTheMiddle: boolean;
  setInTheMiddle: (value: boolean) => void;
  dailyRewardAnimationState: DailyRewardAnimationState;
};

export const useHomeStore = create<HomeStore>()((set, get) => ({
  menuTab: "games",
  setMenuTab: (value) => set({ menuTab: value }),
  homeData: undefined,
  initHomeData: (value) => set({ coins: value.coins, streak: value.streak }),
  coins: 0,
  setCoins: (value) => set({ coins: value }),
  addCoins: (value) => set((state) => ({ coins: state.coins + value })),

  // Daily reward
  coinsCount: 20,
  streak: [],
  coinsFinishCount: 0,
  amountPerCoin: 0,
  fireCoins: false,
  setFireCoins: (value) => set({ fireCoins: value }),
  fireShaking: false,
  incCoinsFinishCount: () => {
    const newValue = get().coinsFinishCount + 1;
    const coinsCount = get().coinsCount;
    if (coinsCount == newValue) {
      set({ coinsFinishCount: 0, fireCoins: false, fireShaking: false });
      return;
    }
    set({ coinsFinishCount: newValue });
  },
  resetCoinsFinishCount: () => set({ coinsFinishCount: 0 }),
  handleCoinFinished: () => {
    get().incCoinsFinishCount();
    get().addCoins(get().amountPerCoin);
  },
  claimCurrentDay: async () => {
    const streak = get().streak;
    const currentDay = streak.find((d) => d.status === "present");
    if (!currentDay) {
      throw new Error("No present day found");
    }
    const newStreak = streak.map((day) =>
      day.status == "present" ? Object.assign(day, { claimed: true }) : day,
    );
    const amountPerCoin = currentDay.reward / 20;

    set({
      streak: newStreak,
      fireShaking: true,
      dailyRewardAnimationState: DailyRewardAnimationState.CARD_SHAKING,
    });
    await sleep(500);
    set({ fireCoins: true, amountPerCoin: amountPerCoin });
    await sleep(3000);
    set({
      fireCoins: false,
      amountPerCoin: 0,
      inTheMiddle: false,
      fireShaking: false,
      dailyRewardAnimationState: DailyRewardAnimationState.FINISHED,
    });
  },
  inTheMiddle: false,
  setInTheMiddle: (value) => set({ inTheMiddle: value }),
  dailyRewardAnimationState: DailyRewardAnimationState.AWAIT,
}));
