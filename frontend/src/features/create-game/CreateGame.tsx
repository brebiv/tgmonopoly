import { useCreateGame } from "@/shared/hooks/useCreateGame";
import { Button } from "@/shared/ui/Button";
import { SelectGroup } from "@/shared/ui/SelectGroup";
import { navigateToGame } from "@/shared/utils";
import { useState } from "react";

export const CreateGame = () => {
  const [numPlayers, setNumPlayers] = useState(2);

  const createGameMutation = useCreateGame();

  const handleCreateGame = async () => {
    createGameMutation.mutate(numPlayers, {
      onSuccess: async (data) => {
        const gameUUID = data.game_uuid;
        navigateToGame(gameUUID);
      },
    });
  };

  return (
    <div className="flex flex-col gap-4">
      <div className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <div className="grid grid-cols-2 gap-8">
            <div className="flex h-18 flex-col gap-2">
              <SelectGroup defaultValue={2} onChange={setNumPlayers} label="Number of players">
                <SelectGroup.Item value={2} />
                <SelectGroup.Item value={3} />
                <SelectGroup.Item value={100} />
              </SelectGroup>
            </div>
            <div className="flex flex-col gap-2">
              <p>Game mode</p>
              <select
                name="game_config"
                className="bg-background border-hint focus:outline-button h-full rounded-md border-[1px] px-2"
              >
                <option value={"classic"}>Classic</option>
              </select>
            </div>
          </div>
        </div>

        {numPlayers}

        <Button onClick={handleCreateGame} disabled={createGameMutation.isPending}>
          {createGameMutation.isPending ? "Creating…" : "Create"}
        </Button>

        {createGameMutation.isError && (
          <p className="text-red-600">{JSON.stringify(createGameMutation.error)}</p>
        )}
      </div>
    </div>
  );
};
