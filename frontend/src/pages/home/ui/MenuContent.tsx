import { CreateGame } from "@/features/create-game/CreateGame";
import { useHomeStore } from "../stores/homeStore";
import { GameList } from "./components/GameList";
// @ts-ignore
import { useEffect, useRef, useState } from "react";
import { useAuthContext } from "@/entities/AuthProvider";
import { TopBaner } from "./components/TopBanner";
import { Gamepad2Icon, UsersRound } from "lucide-react";
import { cn } from "@/shared/utils";

export const MenuContent = () => {
  const menuTab = useHomeStore((s) => s.menuTab);
  const { me } = useAuthContext();

  const scrollerRef = useRef<HTMLDivElement | null>(null);

  return (
    <div id="menu-content" className="flex min-h-0 grow-1 flex-col gap-6">
      {menuTab == "create_game" && <CreateGame />}
      {menuTab == "games" && (
        <>
          <TopBaner />
          <div className="relative flex min-h-0 flex-1 flex-col gap-2 rounded-xl">
            <div className="flex">
              <div className="flex gap-2">
                <div className="flex gap-1">
                  <UsersRound /> 7k
                </div>
                <div className="flex gap-1">
                  <Gamepad2Icon /> 532
                </div>
              </div>
            </div>
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
          </div>
        </>
      )}
    </div>
  );
};
