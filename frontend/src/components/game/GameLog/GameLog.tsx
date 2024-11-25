import { useEventStore } from "@/stores/EventStore";
import { useEffect, useRef } from "react";
import GameLogRow from "./GameLogRow";

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
      {eventLog.map((event, i) => (
        <GameLogRow key={`${event.type}-${i}`} event={event} />
      ))}
    </div>
  );
}

export default GameLog;
