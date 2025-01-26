import { useEventStore } from "@/stores/EventStore";
import { useEffect, useRef } from "react";
import GameLogRow from "./GameLogRow";
import { GameScopeType } from "@/types/api";

function GameLog() {
  const { eventLog } = useEventStore((state) => state);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (containerRef.current) {
      containerRef.current.scrollTop = containerRef.current.scrollHeight;
    }
  }, [eventLog]);

  return (
    <div
      ref={containerRef}
      className="game-log absolute top-0 flex h-full w-full flex-col overflow-y-scroll p-1 text-white"
    >
      {eventLog.filter((event) => event.type !== GameScopeType.GAME_SERVICE).map((event, i) => (
        <GameLogRow key={`${event.type}-${i}`} event={event} />
      ))}
    </div>
  );
}

export default GameLog;
