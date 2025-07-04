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
    <div className="relative flex flex-col gap-4 w-full h-screen pt-2">
      <Header />
      <div className="px-8 flex flex-col gap-6">
        {me.current_game && <CurrentGameCard game={me.current_game} />}
        <div className="grid grid-cols-2 gap-4 justify-evenly">
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
