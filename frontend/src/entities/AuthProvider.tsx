import React, { createContext, useContext } from "react";
import type { Me } from "./types";
import { useMe } from "@/shared/hooks/useMe";
import { AuthErrorScreen } from "@/pages/home/ui/AuthErrorScreen";

interface AuthProviderData {
  me: Me;
  gameUUID?: string;
}

const AuthContext = createContext<AuthProviderData | undefined>(undefined);

interface AuthContextProps {
  currentGameUUIDMustMatchWithURL?: boolean;
  children: React.ReactNode;
}

export const AuthContextProvider: React.FC<AuthContextProps> = ({
  currentGameUUIDMustMatchWithURL,
  children,
}) => {
  const contextValue = {} as AuthProviderData;
  const { isLoading: isMeLoading, isError: isMeError, data: me } = useMe(true, false);
  let gameUUID: string | undefined = undefined;

  if (isMeError) return <AuthErrorScreen />;
  if (isMeLoading) return <h1>Loading auth</h1>;

  if (!me) {
    return;
  }

  if (currentGameUUIDMustMatchWithURL) {
    const pathname = location.pathname;
    const gameUUID = pathname.split("/").filter(Boolean).pop() ?? null;

    if (!gameUUID) {
      console.error("Could not get UUID from url");
      return;
    }

    if (!me.current_game) {
      return <h1>Player is not in the game</h1>;
    } else if (me.current_game.uuid != gameUUID) {
      console.log("currentGameUUIDMustMatch and it didn't ");
      return <h1>Game UUID mismatch</h1>;
    }
    console.log("Performed UUID check, LGTM");
  }

  contextValue.me = me;
  contextValue.gameUUID = gameUUID;

  return <AuthContext.Provider value={contextValue}>{children}</AuthContext.Provider>;
};

export const useAuthContext = (): AuthProviderData => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuthContext must be used within a AuthContextProvider");
  }
  return context;
};
