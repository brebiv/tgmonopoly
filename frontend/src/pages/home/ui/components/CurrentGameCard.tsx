import { Button } from "@/shared/ui/Button";
import { Card } from "@/shared/ui/Card";

export const CurrentGameCard = () => {
  return (
    <Card>
      Current game
      <Button
        onClick={() => {
          location.href = "game/87462c62-2c01-499d-bbc9-26eea8b38c78";
        }}
      >
        Return
      </Button>
    </Card>
  );
};
