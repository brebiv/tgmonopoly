import { create } from "zustand";
import type { Me } from "./types";

type AuthState = {
  me: Me | null;
  setMe: (me: Me) => void;
};

const useAuthStore = create<AuthState>((set) => ({
  me: null,
  setMe: (me: Me) => set({ me }),
}));

export default useAuthStore;
