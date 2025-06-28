import { createGame } from "@/shared/api";
import { Button } from "@/shared/ui/Button";
import { SelectGroup } from "@/shared/ui/SelectGroup";
import { useState } from "react";

export const CreateGame = () => {
  const [numPlayers, setNumPlayers] = useState(2);
  const handleCreateGame = () => {
    createGame(numPlayers);
  };

  return (
    <div className="flex flex-col gap-4">
      <form className="flex flex-col gap-4">
        <div className="flex flex-col gap-2">
          <p>Number of players</p>
          <SelectGroup defaultValue={2} onChange={setNumPlayers}>
            <SelectGroup.Item value={2} />
            <SelectGroup.Item value={3} />
            <SelectGroup.Item value={100} />
          </SelectGroup>
        </div>

        {numPlayers}

        <Button onClick={handleCreateGame}>Create</Button>
      </form>
    </div>
  );
};
