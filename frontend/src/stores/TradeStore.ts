import { getPropertyById } from "@/lib/utils";
import { Ownership } from "@/types/api";
import { create } from "zustand";

export type TradeMenuData = {
  from_player: number;
  to_player: number;
  ownerships: Ownership[] | null;
  cash_given: number;
  cash_received: number;
};

interface TradeStore {
  showTradeMenu: boolean;
  setShowTradeMenu: (showTradeMenu: boolean) => void;
  tradeMenuData: TradeMenuData | null;
  setTradeMenuData: (tradeMenuData: TradeMenuData | null) => void;
  initTradeMenuData: (fromPlayer: number, toPlayer: number) => void;
  addOwnershipToTradeMenu: (newOwnership: Ownership) => void;
  isOwnershipInTradeMenu: (propertyId: number) => boolean;
  removeOwnershipFromTradeMenu: (propertyId: number) => void;
  getValueRecieved: () => number;
  getValueGiven: () => number;
  addCashGiven: (amount: number) => void;
  addCashReceived: (amount: number) => void;
  setCashGiven: (amount: number) => void;
  setCashReceived: (amount: number) => void;
  resetMoneyGiven: () => void;
  resetMoneyReceived: () => void;
  isTradeValid: () => boolean;
  resetTrade: () => void;
  isPreview: boolean;
  setIsPreview: (value: boolean) => void;
}

export const useTradeStore = create<TradeStore>((set, get) => ({
  showTradeMenu: false,
  setShowTradeMenu: (showTradeMenu: boolean) => {
    set({ showTradeMenu });
  },
  tradeMenuData: null,
  setTradeMenuData: (tradeMenuData: TradeMenuData | null) => {
    set({ tradeMenuData });
  },
  initTradeMenuData: (fromPlayer: number, toPlayer: number) => {
    set(() => {
      return {
        tradeMenuData: {
          from_player: fromPlayer,
          to_player: toPlayer,
          ownerships: [],
          cash_given: 0,
          cash_received: 0,
        },
      };
    });
  },
  addOwnershipToTradeMenu: (newOwnership: Ownership) => {
    set((state) => {
      const currentTradeMenuData = state.tradeMenuData;

      if (currentTradeMenuData) {
        return {
          tradeMenuData: {
            ...currentTradeMenuData,
            ownerships: currentTradeMenuData.ownerships
              ? [...currentTradeMenuData.ownerships, newOwnership]
              : [newOwnership],
          },
        };
      } else {
        console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  isOwnershipInTradeMenu: (propertyId: number) => {
    const currentTradeMenuData = get().tradeMenuData;

    if (currentTradeMenuData && currentTradeMenuData.ownerships) {
      return currentTradeMenuData.ownerships.some((ownership) => ownership.property === propertyId);
    } else {
      // console.warn("Trade menu data or ownerships array is not set");
      return false;
    }
  },
  removeOwnershipFromTradeMenu: (propertyId: number) => {
    set((state) => {
      const currentTradeMenuData = state.tradeMenuData;

      if (currentTradeMenuData && currentTradeMenuData.ownerships) {
        return {
          tradeMenuData: {
            ...currentTradeMenuData,
            ownerships: currentTradeMenuData.ownerships.filter(
              (ownership) => ownership.property !== propertyId,
            ),
          },
        };
      } else {
        console.warn("Trade menu data or ownerships array is not set");
        return {};
      }
    });
  },
  getValueGiven: () => {
    const tradeMenuData = get().tradeMenuData;

    if (!tradeMenuData) {
      return 0;
    }

    let totalValue = 0;

    if (tradeMenuData.ownerships) {
      totalValue = tradeMenuData.ownerships.reduce((total, ownership) => {
        const property = getPropertyById(ownership.property);
        if (!property) {
          return total;
        }

        if (ownership.player === tradeMenuData.from_player) {
          total += property.propertyData!.price;
        }
        return total;
      }, 0);
    }

    totalValue += tradeMenuData.cash_given || 0;

    return totalValue;
  },

  getValueRecieved: () => {
    const tradeMenuData = get().tradeMenuData;

    if (!tradeMenuData) {
      return 0;
    }

    let totalValue = 0;

    if (tradeMenuData.ownerships) {
      totalValue = tradeMenuData.ownerships.reduce((total, ownership) => {
        const property = getPropertyById(ownership.property);
        if (!property) {
          return total;
        }

        if (ownership.player === tradeMenuData.to_player) {
          total += property.propertyData!.price;
        }
        return total;
      }, 0);
    }

    totalValue += tradeMenuData.cash_received || 0;

    return totalValue;
  },
  addCashGiven: (amount: number) => {
    set((state) => {
      const currentTradeMenuData = state.tradeMenuData;

      if (currentTradeMenuData) {
        return {
          tradeMenuData: {
            ...currentTradeMenuData,
            cash_given: currentTradeMenuData.cash_given + amount,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  addCashReceived: (amount: number) => {
    set((state) => {
      const currentTradeMenuData = state.tradeMenuData;

      if (currentTradeMenuData) {
        return {
          tradeMenuData: {
            ...currentTradeMenuData,
            cash_received: currentTradeMenuData.cash_received + amount,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  setCashGiven: (amount: number) => {
    set((current) => {
      if (current.tradeMenuData) {
        return {
          ...current,
          tradeMenuData: {
            ...current.tradeMenuData,
            cash_given: amount,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  setCashReceived: (amount: number) => {
    set((current) => {
      if (current.tradeMenuData) {
        return {
          ...current,
          tradeMenuData: {
            ...current.tradeMenuData,
            cash_received: amount,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  resetMoneyGiven: () => {
    set((current) => {
      if (current.tradeMenuData) {
        return {
          ...current,
          tradeMenuData: {
            ...current.tradeMenuData,
            cash_given: 0,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  resetMoneyReceived: () => {
    set((current) => {
      if (current.tradeMenuData) {
        return {
          ...current,
          tradeMenuData: {
            ...current.tradeMenuData,
            cash_received: 0,
          },
        };
      } else {
        // console.warn("Trade menu data is not set");
        return {};
      }
    });
  },
  isTradeValid: () => {
    const { tradeMenuData, getValueGiven, getValueRecieved } = get();
    if (!tradeMenuData) {
      return false;
    }
    return getValueGiven() > 0 && getValueRecieved() > 0;
  },
  resetTrade: () => {
    set({ tradeMenuData: null });
  },
  isPreview: false,
  setIsPreview(value: boolean) {
    set({ isPreview: value });
  },
}));
