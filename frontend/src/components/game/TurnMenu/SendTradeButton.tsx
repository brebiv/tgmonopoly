import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { useTradeStore } from "@/stores/TradeStore";
import { GameActionType } from "@/types/api";
import { HandshakeIcon } from "lucide-react";

function SendTradeButton({ gameUUID, disabled }: { gameUUID: string; disabled?: boolean }) {
  const { tradeMenuData } = useTradeStore();

  return (
    <Button
      variant={"default"}
      onClick={() => {
        sendGameAction({
          action: GameActionType.CREATE_TRADE,
          game_uuid: gameUUID,
          extra_data: {
            from_player: tradeMenuData?.from_player,
            to_player: tradeMenuData?.to_player,
            cash_given: tradeMenuData?.cash_given,
            cash_received: tradeMenuData?.cash_received,
            ownerships: tradeMenuData?.ownerships?.map((ownership) => ownership.id),
          },
        });
      }}
      disabled={disabled}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <HandshakeIcon />
      {"Send trade"}
    </Button>
  );
}

export default SendTradeButton;
