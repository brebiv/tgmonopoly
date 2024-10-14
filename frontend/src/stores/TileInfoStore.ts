import { Tile } from "@/types/api";
import { create } from "zustand";

interface TileInfoStore {
  tile: Tile | null;
  tileRef: React.RefObject<HTMLDivElement> | null;
  setTileInfo: (tile: Tile | null, tileRef: React.RefObject<HTMLDivElement> | null) => void;
}

// @ts-ignore
export const useTileInfoStore = create<TileInfoStore>((set, get) => ({
  tile: null,
  tileRef: null,
  setTileInfo: (tile: Tile | null, tileRef: React.RefObject<HTMLDivElement> | null) => {
    set({ tile: tile, tileRef: tileRef });
  },
}));
