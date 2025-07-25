import { useWebSocketContext } from "@/app/providers/WebSocketProvider";
import { Button } from "@/shared/ui/Button";
import { GavelIcon } from "lucide-react";

interface StartAuctionButtonProps {
  protocol?: "ws" | "http";
}

export const StartAuctionButton = ({ protocol = "ws" }: StartAuctionButtonProps) => {
  const { sendJSON } = useWebSocketContext();

  const handleClickWS = () => {
    const command = { action: "start_auction" };
    sendJSON(command);
  };

  const handleClickHTTP = () => {
    console.error("Not implemented");
  };

  return (
    <Button
      className="bg-destructive flex gap-2 py-3 text-lg font-semibold"
      onClick={protocol == "ws" ? handleClickWS : handleClickHTTP}
    >
      <GavelIcon /> {"Auction"}
    </Button>
  );
};
