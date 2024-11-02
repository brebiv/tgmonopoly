import { sendGameAction } from "@/api";
import { Button } from "@/components/ui/button";
import { GameActionType } from "@/types/api";

function RejectButton({ gameUUID, disabled }: { gameUUID: string; disabled?: boolean }) {
  return (
    <Button
      variant={"destructive"}
      onClick={() => {
        sendGameAction({ action: GameActionType.REJECT, game_uuid: gameUUID });
      }}
      className="w-full gap-2 py-6 text-lg font-semibold"
      disabled={disabled}
    >
      <p>{"Reject"}</p>
    </Button>
  );
}

export default RejectButton;
