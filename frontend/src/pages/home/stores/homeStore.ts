import { create } from "zustand";

type MenuTabs = "games" | "friends" | "store" | "create_game";

type HomeStore = {
  menuTab: MenuTabs;
  setMenuTab: (value: MenuTabs) => void;
};

export const useHomeStore = create<HomeStore>()((set) => ({
  menuTab: "games",
  setMenuTab: (value) => set({ menuTab: value }),
}));
