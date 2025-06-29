import { Button } from "@/shared/ui/Button";

export const CurrentGameCard = () => {
  return (
    <div className="text-2xl border-[1px] border-hint rounded-lg px-4 py-2 flex flex-col gap-4">
      Current game
      <Button
        onClick={() => {
          location.href = "game/87462c62-2c01-499d-bbc9-26eea8b38c78";
        }}
      >
        Return
      </Button>
    </div>
  );
};
