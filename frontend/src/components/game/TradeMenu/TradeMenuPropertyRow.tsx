import SolarPowerIcon from "@/components/ui/icons/SolorPowerIcon";
import WindPowerIcon from "@/components/ui/icons/WindPowerIcon";
import { useTheme } from "@/stores/ThemeContext";
import { SVGIcons, Tile } from "@/types/api";
import { AtomIcon, DamIcon } from "lucide-react";

function TradeMenuPropertyRow({ tile }: { tile: Tile }) {
  const { hintColor } = useTheme();

  const renderIcon = (svgIcon: SVGIcons | string) => {
    switch (svgIcon) {
      case SVGIcons.WIND_POWER:
        return <WindPowerIcon className="h-full" fill="black" outline="" />;
      case SVGIcons.DAM:
        return <DamIcon className="h-full" />;
      case SVGIcons.SOLAR_POWER:
        return <SolarPowerIcon className="h-full" fill="black" outline="" />;
      case SVGIcons.NUKE:
        return <AtomIcon className="h-full" />;
      default:
        return null;
    }
  };

  return (
    <div className="my-1 grid h-8 w-full grid-cols-2 items-center gap-2">
      <div className="">
        {tile.propertyData?.svg_icon ? (
          renderIcon(tile.propertyData.svg_icon)
        ) : (
          <img src={tile.propertyData?.icon} className="max-h-8" />
        )}
      </div>
      <div className="flex flex-col overflow-clip">
        <h3 className="font-bold" style={{ color: tile?.propertyData?.group_color }}>
          {tile?.name &&
            (tile.name.split(" ").length === 2
              ? tile.name
                  .split(" ")
                  .map((word) => word[0].toUpperCase())
                  .join(".")
              : tile.name)}{" "}
        </h3>
        <h3 className="text-xs font-thin" style={{ color: hintColor }}>
          ${tile?.propertyData?.price}
        </h3>
      </div>
    </div>
  );
}

export default TradeMenuPropertyRow;
