import { create } from "zustand";

interface LayoutStore {
  boardCenterPaddingX: number;
  boardCenterPaddingY: number;
  setBoardCenterPaddingX: (boardCenterPaddingX: number) => void;
  setBoardCenterPaddingY: (boardCenterPaddingY: number) => void;
}

// @ts-ignore
export const useLayoutStore = create<LayoutStore>((set, get) => ({
  boardCenterPaddingX: 0,
  boardCenterPaddingY: 0,
  setBoardCenterPaddingX: (boardCenterPaddingX: number) => {
    set({ boardCenterPaddingX });
  },
  setBoardCenterPaddingY: (boardCenterPaddingY: number) => {
    set({ boardCenterPaddingY });
  },
}));
