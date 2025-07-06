import { NavButton } from "@/shared/ui/NavButton";
import { useAuth } from "../../../shared/hooks/useAuth";
import { AuthErrorScreen } from "./AuthErrorScreen";
import { GameList } from "./components/GameList";
import { Header } from "./components/Header";
import { LoadingScreen } from "./LoadingScreen";
import { useState } from "react";
import { CreateGame } from "@/features/create-game/CreateGame";
import { CurrentGameCard } from "./components/CurrentGameCard";

export const HomePage = () => {
  const [activeTab, setActiveTab] = useState<"list" | "create">("list");
  const { isPending, isError, data: me } = useAuth(true, true);

  if (isPending) {
    return <LoadingScreen />;
  }

  if (isError) {
    return <AuthErrorScreen />;
  }

  return (
    <div className="bg-secondary-background relative flex h-screen w-full flex-col gap-4 pt-2">
      <Header />
      <div className="flex flex-col gap-6 px-8">
        {me.current_game && <CurrentGameCard game={me.current_game} />}
        <div className="grid grid-cols-2 justify-evenly gap-4">
          <NavButton
            active={activeTab == "list"}
            text="Game list"
            onClick={() => {
              setActiveTab("list");
            }}
          />
          <NavButton
            disabled={me.current_game != null}
            active={activeTab == "create"}
            text="Create game"
            onClick={() => {
              setActiveTab("create");
            }}
          />
        </div>
        {activeTab == "list" && <GameList />}
        {activeTab == "create" && <CreateGame />}
      </div>
    </div>
  );
};
