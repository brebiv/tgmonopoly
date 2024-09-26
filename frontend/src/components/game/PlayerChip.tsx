function PlayerChip({
  color,
  left,
  top,
}: {
  color: string;
  left: number | undefined;
  top: number | undefined;
}) {
  return (
    <div
      className="absolute z-10 h-3 w-3 rounded-full"
      style={{ backgroundColor: color, left: left, top: top }}
    ></div>
  );
}

export default PlayerChip;
