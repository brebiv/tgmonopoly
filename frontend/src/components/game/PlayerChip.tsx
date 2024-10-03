import { PLAYER_CHIP_MOVE_DURATION_MS, PLAYER_CHIP_COLORS } from "@/config";

function PlayerChip({
  color,
  left,
  top,
}: {
  color: string;
  left: number | undefined;
  top: number | undefined;
}) {
  const [primaryColor, borderColor] = PLAYER_CHIP_COLORS[color as keyof typeof PLAYER_CHIP_COLORS];
  return (
    <div
      className="absolute z-10 h-3 w-3 rounded-full outline outline-2"
      style={{
        backgroundColor: primaryColor,
        outlineColor: borderColor,
        left: left,
        top: top,
        transition: `left ${PLAYER_CHIP_MOVE_DURATION_MS}ms, top ${PLAYER_CHIP_MOVE_DURATION_MS}ms`,
        // boxShadow: `0px 0px 8px 2px rgba(0,0,0,0.55)`,
      }}
    ></div>
  );
}

export default PlayerChip;
