import ThemedDiv from "../../ui/ThemedDiv";
import { cn, getPlayerById } from "@/lib/utils";
import { useMemo, useState } from "react";
import PlayerNameSpan from "../GameLog/PlayerNameSpan";
import { useTiles } from "@/hooks";
import TradeMenuPropertyRow from "./TradeMenuPropertyRow";
import { useTradeStore } from "@/stores/TradeStore";
import { useTheme } from "@/stores/ThemeContext";
import { PlusIcon, XIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import AddMoneyToTradeDialog from "./AddMoneyToTradeDialog";

function TradeMenu({ orientation = "horizontal" }: { orientation?: "vertical" | "horizontal" }) {
  const {
    tradeMenuData,
    getValueGiven,
    getValueRecieved,
    resetMoneyGiven,
    resetMoneyReceived: resetMoneyRecieved,
    isPreview,
  } = useTradeStore();
  const { data: tiles } = useTiles();
  const { hintColor } = useTheme();

  const [showAddMoneyToTradeDialog, setShowAddMoneyToTradeDialog] = useState(false);
  const [isGivingMoney, setIsGivingMoney] = useState(false);

  if (!tradeMenuData) {
    return null;
  }

  const fromPlayer = useMemo(() => getPlayerById(tradeMenuData.from_player), [tradeMenuData]);
  const toPlayer = useMemo(() => getPlayerById(tradeMenuData.to_player), [tradeMenuData]);
  const tilesToGive = useMemo(
    () =>
      tradeMenuData.ownerships
        ?.filter((o) => o.player === fromPlayer?.id)
        .map((o) => tiles?.find((t) => t.propertyData?.id === o.property)),
    [tradeMenuData],
  );

  const tilesToRecieve = useMemo(
    () =>
      tradeMenuData.ownerships
        ?.filter((o) => o.player === toPlayer?.id)
        .map((o) => tiles?.find((t) => t.propertyData?.id === o.property)),
    [tradeMenuData],
  );

  return (
    <ThemedDiv className="trade-menu aboslute top-0 flex h-full w-full flex-col items-center gap-2 overflow-y-scroll p-2">
      <AddMoneyToTradeDialog
        open={showAddMoneyToTradeDialog}
        setOpen={setShowAddMoneyToTradeDialog}
        isGivingMoney={isGivingMoney}
      />
      {/* <h1 className="text-center text-lg font-semibold">
        {"Trade with "} <PlayerNameSpan player={toPlayer!} />
      </h1> */}
      {/* Column 1 */}
      <div
        className={cn(
          "flex w-full grow overflow-x-hidden",
          orientation === "vertical" ? "flex-col" : "flex-row gap-1",
        )}
      >
        <div className="flex w-1/2 flex-col gap-2">
          {!isPreview && (
            <Button
              variant={"default"}
              className="h-auto p-0 pr-1"
              onClick={() => {
                setIsGivingMoney(true);
                setShowAddMoneyToTradeDialog(true);
              }}
            >
              <PlusIcon className="w-5" />$
            </Button>
          )}
          <h3>{"You give: "}</h3>
          {isPreview ? (
            <>
              {tradeMenuData.cash_received > 0 && (
                <h1 className="flex">
                  <span style={{ color: hintColor }}>$ </span>
                  {tradeMenuData.cash_received}
                </h1>
              )}
              {tilesToRecieve?.map((p, i) => <TradeMenuPropertyRow key={i} tile={p!} />)}
            </>
          ) : (
            <>
              {tradeMenuData.cash_given > 0 && (
                <h1 className="flex">
                  <span style={{ color: hintColor }}>$ </span>
                  {tradeMenuData.cash_given}
                  <XIcon
                    className="ml-auto"
                    onClick={() => {
                      resetMoneyGiven();
                    }}
                  />
                </h1>
              )}
              {tilesToGive?.map((p, i) => <TradeMenuPropertyRow key={i} tile={p!} />)}
            </>
          )}
        </div>

        {/* Column 2 */}
        <div className="flex w-1/2 flex-col gap-2">
          {!isPreview && (
            <Button
              variant={"default"}
              className="h-auto p-0 pr-1"
              onClick={() => {
                setIsGivingMoney(false);
                setShowAddMoneyToTradeDialog(true);
              }}
            >
              <PlusIcon className="w-5" />$
            </Button>
          )}

          {isPreview ? (
            <>
              <h3>
                <PlayerNameSpan player={fromPlayer!} /> {"gives: "}
              </h3>
              {tradeMenuData.cash_given > 0 && (
                <h1 className="flex">
                  <span style={{ color: hintColor }}>$ </span>
                  {tradeMenuData.cash_given}
                </h1>
              )}
              {tilesToGive?.map((p, i) => <TradeMenuPropertyRow key={i} tile={p!} />)}
            </>
          ) : (
            <>
              <h3>
                <PlayerNameSpan player={toPlayer!} /> {"gives: "}
              </h3>
              {tradeMenuData.cash_received > 0 && (
                <h1 className="flex">
                  <span style={{ color: hintColor }}>$ </span>
                  {tradeMenuData.cash_received}
                  <XIcon className="ml-auto" onClick={() => resetMoneyRecieved()} />
                </h1>
              )}
              {tilesToRecieve?.map((p, i) => <TradeMenuPropertyRow key={i} tile={p!} />)}
            </>
          )}
        </div>
      </div>
      <div className="flex w-full flex-col items-center gap-2">
        <div className="flex w-full justify-center font-thin">
          <div className="flex grow justify-center gap-1">
            <h2>
              <span style={{ color: hintColor }}>$ </span>
              {isPreview ? getValueRecieved() : getValueGiven()}
            </h2>
            {/* <Button variant={"default"} className="h-auto p-0">
              <PlusIcon className="w-5" />
            </Button> */}
          </div>
          <div className="flex grow-[2] justify-center">
            <h2>{"Total value"}</h2>
          </div>
          <div className="flex grow justify-center gap-1">
            <h2>
              <span style={{ color: hintColor }}>$ </span>
              {isPreview ? getValueGiven() : getValueRecieved()}
            </h2>
            {/* <Button variant={"default"} className="h-auto p-0">
              <PlusIcon className="w-5" />
            </Button> */}
          </div>
        </div>
      </div>
    </ThemedDiv>
  );
}

export default TradeMenu;
