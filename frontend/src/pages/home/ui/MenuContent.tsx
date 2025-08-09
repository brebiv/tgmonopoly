import { CreateGame } from "@/features/create-game/CreateGame";
import { useHomeStore } from "../stores/homeStore";
// import { GameList } from "./components/GameList";
// @ts-ignore
import { useEffect, useRef, useState } from "react";
// import { useAuthContext } from "@/entities/AuthProvider";
import { TopBaner } from "./components/TopBanner";
// import { cn } from "@/shared/utils";
import { MainMenu } from "./components/MainMenu";

export const MenuContent = () => {
  const menuTab = useHomeStore((s) => s.menuTab);
  // const { me } = useAuthContext();

  // const scrollerRef = useRef<HTMLDivElement | null>(null);

  return (
    <div id="menu-content" className="flex min-h-0 grow-1 flex-col gap-6">
      {menuTab == "create_game" && <CreateGame />}
      {menuTab == "games" && (
        <>
          <TopBaner />
          <MainMenu />
          {/* <div className="relative flex min-h-0 flex-1 flex-col gap-2 rounded-xl">
            <div
              ref={scrollerRef}
              className={cn("relative min-h-0 overflow-y-auto overscroll-contain rounded-lg", {
                "overflow-hidden": me.current_game != null,
              })}
            >
              {me.current_game != null && (
                <div className="bg-background absolute z-10 h-full w-full opacity-70"></div>
              )}
              <GameList disabled={me.current_game != null} />
            </div>
          </div> */}
        </>
      )}
    </div>
  );
};
