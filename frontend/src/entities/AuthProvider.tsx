import React, { createContext, useContext } from "react";
import type { Me } from "./types";
import { useMe } from "@/shared/hooks/useMe";

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
  const { isLoading: isMeLoading, isError: isMeError, data: me } = useMe(true, true);
  let gameUUID: string | undefined = undefined;

  if (isMeLoading) return <h1>Loading auth</h1>;
  if (isMeError || !me) return <h1>Error with auth</h1>;

  if (currentGameUUIDMustMatchWithURL) {
    const pathname = URL.parse(location.href)?.pathname;
    gameUUID = pathname?.split("/").pop();

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
