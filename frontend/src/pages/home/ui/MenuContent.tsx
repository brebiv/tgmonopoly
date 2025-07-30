import { CreateGame } from "@/features/create-game/CreateGame";
import { useHomeStore } from "../stores/homeStore";
import { GameList } from "./components/GameList";
import { useEffect, useRef, useState } from "react";
import { useAuthContext } from "@/entities/AuthProvider";
import { TopBaner } from "./components/TopBanner";

export const MenuContent = () => {
  const menuTab = useHomeStore((s) => s.menuTab);
  const { me } = useAuthContext();

  const fadeSize = 12; // px
  const fadeColor = Telegram.WebApp.themeParams.bg_color;
  const threshold = 1;

  const scrollerRef = useRef<HTMLDivElement | null>(null);
  const [atTop, setAtTop] = useState(true);
  const [atBottom, setAtBottom] = useState(false);

  const topFadeStyle: React.CSSProperties = {
    pointerEvents: "none",
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: `${fadeSize}px`,
    borderRadius: "inherit",
    background: `linear-gradient(to bottom, ${fadeColor} 0%, rgba(0,0,0,0) 100%)`,
    opacity: atTop ? 0 : 1,
  };

  const bottomFadeStyle: React.CSSProperties = {
    pointerEvents: "none",
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: `${fadeSize}px`,
    borderRadius: "inherit",
    background: `linear-gradient(to top, ${fadeColor} 0%, rgba(0,0,0,0) 100%`,
    opacity: atBottom ? 0 : 1,
  };

  useEffect(() => {
    const el = scrollerRef.current;
    if (!el) return;

    const update = () => {
      const maxScroll = el.scrollHeight - el.clientHeight;
      const top = el.scrollTop <= threshold;
      const bottom = el.scrollTop >= maxScroll - threshold || maxScroll <= threshold;
      setAtTop(top);
      setAtBottom(bottom);
    };

    update();
    el.addEventListener("scroll", update, { passive: true });
    const ro = new ResizeObserver(update);
    ro.observe(el);

    return () => {
      el.removeEventListener("scroll", update);
      ro.disconnect();
    };
  }, [threshold]);

  return (
    <div id="menu-content" className="flex grow-1 flex-col gap-6 overflow-y-auto">
      {menuTab == "create_game" && <CreateGame />}
      {menuTab == "games" && (
        <>
          <TopBaner />
          {/* <div className="h-32 w-full bg-amber-50 ">Банерочок</div> */}
          <div className="relative min-h-0 flex-1 rounded-xl">
            {/* Scrollable list area */}
            <div ref={scrollerRef} className="h-full overflow-y-auto overscroll-contain rounded-lg">
              <GameList disabled={me.current_game != null} />
            </div>

            {/* Top & bottom gradient fades (always visible) */}
            <div aria-hidden style={topFadeStyle} />
            <div aria-hidden style={bottomFadeStyle} />
          </div>
        </>
      )}
    </div>
  );
};
