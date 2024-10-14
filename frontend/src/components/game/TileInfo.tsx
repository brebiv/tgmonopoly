import { useLayoutStore } from "@/stores/LayoutStore";
import { useTileInfoStore } from "@/stores/TileInfoStore";
import { Card, CardContent, CardHeader } from "../ui/card";
// @ts-ignore
import { CircleX, House, X } from "lucide-react";
import HouseIcon from "./HouseIcon";

function TileInfo() {
  // @ts-ignore
  const { tile, tileRef, setTileInfo } = useTileInfoStore();
  const { boardCenterPaddingX, boardCenterPaddingY } = useLayoutStore();

  if (tile == null) {
    return null;
  }

  return (
    <div
      className="absolute z-10 aspect-square w-full"
      style={{
        padding: `${boardCenterPaddingY}px ${boardCenterPaddingX}px`,
        paddingBottom: `${boardCenterPaddingY + 4}px`,
      }}
    >
      <div className="h-full w-full overflow-y-scroll p-1">
        <Card className="overflow-scroll">
          <CardHeader
            className="flex-row items-center rounded-t-lg px-3 py-2 text-lg"
            style={{
              backgroundColor: tile.propertyData?.group_color,
              color:
                // @ts-ignore
                window.Telegram.WebApp.themeParams.text_color || "white",
            }}
          >
            {tile.name}
            <div
              className="ml-auto"
              onClick={() => {
                setTileInfo(null, null);
              }}
            >
              {/* <X /> */}
              <CircleX />
            </div>
          </CardHeader>
          <CardContent className="px-3 pt-2">
            <div className="flex flex-col gap-1">
              {tile.propertyData != null && (
                <>
                  <div className="flex text-sm">
                    <p className="font-extralight">{"Base rent"}</p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="flex text-sm">
                    <p className="font-thin">
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent_with_1_house}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="flex text-sm">
                    <p className="flex font-thin">
                      <HouseIcon />
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent_with_2_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="flex text-sm">
                    <p className="flex font-thin">
                      <HouseIcon />
                      <HouseIcon />
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent_with_3_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="flex text-sm">
                    <p className="flex font-thin">
                      <HouseIcon />
                      <HouseIcon />
                      <HouseIcon />
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent_with_4_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="flex text-sm">
                    <p className="flex font-thin text-red-500">
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData?.rent_with_5_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </div>
                  <div className="pt-2">
                    <div className="flex text-sm">
                      <p className="flex font-extralight">{"Property price"}</p>
                      <p className="ml-auto">
                        {tile.propertyData?.price}
                        <span className="font-thin"> $</span>
                      </p>
                    </div>
                    <div className="flex text-sm">
                      <p className="flex font-extralight">{"Mortage value"}</p>
                      <p className="ml-auto">
                        {tile.propertyData?.mortgage_value}
                        <span className="font-thin"> $</span>
                      </p>
                    </div>
                    <div className="flex text-sm">
                      <p className="flex font-extralight">{"Buyout price"}</p>
                      <p className="ml-auto">
                        {12412}
                        <span className="font-thin"> $</span>
                      </p>
                    </div>
                    <div className="flex text-sm">
                      <p className="flex font-extralight">{"House price"}</p>
                      <p className="ml-auto">
                        {tile.propertyData?.house_price}
                        <span className="font-thin"> $</span>
                      </p>
                    </div>
                  </div>
                </>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}

export default TileInfo;
