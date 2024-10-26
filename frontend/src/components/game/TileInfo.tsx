import { useTileInfoStore } from "@/stores/TileInfoStore";
import { Card, CardContent, CardHeader } from "../ui/card";
// @ts-ignore
import { CircleX, House, LockOpen, X } from "lucide-react";
import HouseIcon from "./HouseIcon";
import { useOwnerships } from "@/hooks";
import { useEffect, useState } from "react";
import { useGameStore } from "@/stores/GameStore";
import { Button } from "../ui/button";
import { sendGameAction } from "@/api";
import { GameActionType, Ownership } from "@/types/api";
import { hexToRGBA } from "@/lib/utils";
import { useTheme } from "@/stores/ThemeContext";

function TileInfoRow({ children }: { children: React.ReactNode }) {
  return <div className="flex items-center text-sm">{children}</div>;
}

function HousesRow({ amount }: { amount: number }) {
  return (
    <p className="flex font-thin">
      {[...Array(amount)].map((_, i) => (
        <HouseIcon key={i} />
      ))}
    </p>
  );
}

function TileInfo() {
  // @ts-ignore
  const { tile, tileRef, setTileInfo } = useTileInfoStore();
  const { data: ownerships } = useOwnerships();
  const { me, myTurn } = useGameStore((state) => state);

  const [imOwner, setImOwner] = useState(false);
  const [mortgaged, setMortgaged] = useState<boolean>(false);
  const [ownership, setOwnership] = useState<Ownership | null>(null);

  const gameUUID = window.location.pathname.split("/")[2];

  const { textColor, secondaryBGColor } = useTheme();

  useEffect(() => {
    if (!me || !tile || !ownerships) {
      return;
    }

    if (ownerships.length > 0) {
      console.log(tile);

      let ownership = ownerships.find(
        (ownership) => ownership.player === me?.id && ownership.property === tile.propertyData?.id,
      );

      if (ownership) {
        setOwnership(ownership);
        setImOwner(true);
        setMortgaged(ownership.mortgaged);
      } else {
        setOwnership(null);
        setImOwner(false);
        setMortgaged(false);
      }
    }
  }, [ownerships, tile, me]);

  if (tile == null) {
    return null;
  }

  const secondary_bg_color = secondaryBGColor;
  const fallback_bg_color = "rgb(18, 17, 19)";
  const fallback_bg_color_transparent = "rgb(18, 17, 19, 0)";

  const housesButtons: React.ReactNode[] = [];

  if (ownership) {
    if (ownership.can_build_house) {
      housesButtons.push(
        <Button
          className="relative flex-grow gap-2 bg-green-500"
          disabled={!myTurn}
          onClick={() => {
            sendGameAction({
              action: GameActionType.BUY_HOUSE,
              game_uuid: gameUUID,
              extra_data: {
                property_id: tile.propertyData?.id,
              },
            });
            setTileInfo(null, null);
          }}
        >
          {"Buy house"}
        </Button>,
      );
    }

    if (ownership.can_sell_house) {
      housesButtons.push(
        <Button
          variant={"destructive"}
          className="relative flex-grow gap-2"
          disabled={!myTurn}
          onClick={() => {
            sendGameAction({
              action: GameActionType.SELL_HOUSE,
              game_uuid: gameUUID,
              extra_data: {
                property_id: tile.propertyData?.id,
              },
            });
            setTileInfo(null, null);
          }}
        >
          {"Sell house"}
        </Button>,
      );
    }
  }

  return (
    <>
      <div
        className="absolute z-10 h-2 w-full"
        style={{
          backgroundImage: `linear-gradient(
          180deg,
          ${secondary_bg_color || fallback_bg_color} -10%,
          ${hexToRGBA(secondary_bg_color, 0) || fallback_bg_color_transparent} 100%)`,
        }}
      ></div>
      <div className="h-full w-full overflow-y-scroll p-1">
        <Card>
          <CardHeader
            className="flex-row items-center rounded-t-lg px-3 py-2 text-lg"
            style={{
              backgroundColor: tile.propertyData?.group_color,
              color: textColor,
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
          <CardContent className="px-3 pt-3">
            {housesButtons.length > 0 && <div className="mb-2 flex gap-3">{housesButtons}</div>}
            <div className="flex flex-col gap-1">
              {tile.propertyData != null && (
                <>
                  <TileInfoRow>
                    <p className="font-extralight">{"Base rent"}</p>
                    <p className="ml-auto">
                      {tile.propertyData.rent}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <TileInfoRow>
                    <HousesRow amount={1} />
                    <p className="ml-auto">
                      {tile.propertyData.rent_with_1_house}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <TileInfoRow>
                    <HousesRow amount={2} />
                    <p className="ml-auto">
                      {tile.propertyData.rent_with_2_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <TileInfoRow>
                    <HousesRow amount={3} />
                    <p className="ml-auto">
                      {tile.propertyData.rent_with_3_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <TileInfoRow>
                    <HousesRow amount={4} />
                    <p className="ml-auto">
                      {tile.propertyData.rent_with_4_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <TileInfoRow>
                    <p className="flex font-thin text-red-500">
                      <HouseIcon />
                    </p>
                    <p className="ml-auto">
                      {tile.propertyData.rent_with_5_houses}
                      <span className="font-thin"> $</span>
                    </p>
                  </TileInfoRow>
                  <div className="pt-2">
                    <TileInfoRow>
                      <p className="flex font-extralight">{"Property price"}</p>
                      <p className="ml-auto">
                        {tile.propertyData.price}
                        <span className="font-thin"> $</span>
                      </p>
                    </TileInfoRow>
                    <TileInfoRow>
                      <p className="flex font-extralight">{"Mortage value"}</p>
                      <p className="ml-auto">
                        {tile.propertyData.mortgage_value}
                        <span className="font-thin"> $</span>
                      </p>
                    </TileInfoRow>
                    <TileInfoRow>
                      <p className="flex font-extralight">{"Buyout price"}</p>
                      <p className="ml-auto">
                        {tile.propertyData.buyout_price}
                        <span className="font-thin"> $</span>
                      </p>
                    </TileInfoRow>
                    <TileInfoRow>
                      <p className="flex font-extralight">{"House price"}</p>
                      <p className="ml-auto">
                        {tile.propertyData.house_price}
                        <span className="font-thin"> $</span>
                      </p>
                    </TileInfoRow>
                  </div>
                </>
              )}
              {imOwner && (
                <div className="mt-4 flex gap-2">
                  <Button
                    variant={mortgaged ? "default" : "destructive"}
                    className="relative flex-grow gap-2"
                    disabled={!myTurn}
                    onClick={() => {
                      sendGameAction({
                        action: mortgaged
                          ? GameActionType.BUYOUT_PROPERTY
                          : GameActionType.MORTAGE_PROPERTY,
                        game_uuid: gameUUID,
                        extra_data: {
                          property_id: tile.propertyData?.id,
                        },
                      });
                      setTileInfo(null, null);
                    }}
                  >
                    {mortgaged ? (
                      <>
                        <LockOpen />
                        {"Buy out"}
                      </>
                    ) : (
                      "Mortgage"
                    )}
                  </Button>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      </div>
      <div
        className="absolute bottom-0 z-10 h-2 w-full"
        style={{
          backgroundImage: `linear-gradient(
          0deg,
          ${secondary_bg_color || fallback_bg_color} -10%,
          ${hexToRGBA(secondary_bg_color, 0) || fallback_bg_color_transparent} 110%)`,
        }}
      ></div>
    </>
  );
}

export default TileInfo;
