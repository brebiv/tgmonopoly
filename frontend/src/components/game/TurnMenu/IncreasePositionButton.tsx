import { Button } from "@/components/ui/button";
import { useGameStore } from "@/stores/GameStore";

function IncreasePositionButton() {
  return (
    <Button
      variant={"default"}
      onClick={() => {
        const { players, setPlayers } = useGameStore.getState();
        if (players && players.length > 0) {
          const updatedPlayers = players.map((player, index) => {
            if (index === 0) {
              return { ...player, position: (player.position + 1) % 40 };
            }
            return player;
          });
          setPlayers(updatedPlayers);
        }
      }}
    >
      Position + 1
    </Button>
  );
}

export default IncreasePositionButton;
