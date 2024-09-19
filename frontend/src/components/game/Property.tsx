import { Tile } from "@/types/api";

interface PropertyProps {
  tile: Tile;
}

function Property({ tile }: PropertyProps) {
  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center">
      <img src={tile.propertyData?.icon} className="-rotate-90" />
      {/* Group color marker */}
      <div
        className="absolute -top-1 h-1 w-full"
        style={{ backgroundColor: tile.propertyData?.group_color }}
      ></div>
    </div>
  );
}

export default Property;
