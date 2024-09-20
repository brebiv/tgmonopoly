import { Tile } from "@/types/api";

interface PropertyProps {
  tile: Tile;
}

function Property({ tile }: PropertyProps) {
  let side: "top" | "right" | "bottom" | "left" | undefined = undefined;

  if (tile.position >= 0 && tile.position < 10) {
    side = "top";
  } else if (tile.position >= 10 && tile.position < 20) {
    side = "right";
  } else if (tile.position >= 20 && tile.position < 30) {
    side = "bottom";
  } else if (tile.position >= 30 && tile.position < 40) {
    side = "left";
  }

  return (
    <div className="relative flex h-full w-full flex-col items-center justify-center p-1">
      {(side == "top" || side == "bottom") && (
        <img src={tile.propertyData?.icon} className="-rotate-90" />
      )}
      {(side == "right" || side == "left") && (
        <img src={tile.propertyData?.icon} className="h-full" />
      )}
      {/* Group color marker */}
      <div
        className={
          side === "top"
            ? "absolute -top-3 h-3 w-full"
            : side === "right"
              ? "absolute -right-3 h-full w-3"
              : side === "bottom"
                ? "absolute -bottom-3 h-3 w-full"
                : side === "left"
                  ? "absolute -left-3 h-full w-3"
                  : ""
        }
        style={{
          backgroundColor: `var(--group-color-${tile.propertyData?.group_id})`,
        }}
      >
        <div
          className="flex h-full w-full items-center justify-center"
          style={{
            color:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.text_color || "red",
          }}
        >
          {(side == "top" || side == "bottom") && (
            <p className="text-xs">{tile.propertyData?.price}</p>
          )}
          {side == "right" && (
            <p className="rotate-90 text-xs">{tile.propertyData?.price}</p>
          )}
          {side == "left" && (
            <p className="-rotate-90 text-xs">{tile.propertyData?.price}</p>
          )}
        </div>
      </div>
    </div>
  );
}

export default Property;
