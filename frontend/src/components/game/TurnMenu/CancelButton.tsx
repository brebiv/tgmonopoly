import { Button } from "@/components/ui/button";
import { useTradeStore } from "@/stores/TradeStore";
import { OctagonXIcon } from "lucide-react";

function CancelButton({ disabled }: { disabled?: boolean }) {
  const { setShowTradeMenu, setTradeMenuData } = useTradeStore();
  return (
    <Button
      variant={"destructive"}
      onClick={() => {
        setShowTradeMenu(false);
        setTradeMenuData(null);
      }}
      disabled={disabled}
      className="w-full gap-2 py-6 text-lg font-semibold"
    >
      <OctagonXIcon />
      {"Cancel"}
    </Button>
  );
}

export default CancelButton;
