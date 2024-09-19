import { useEffect, useState } from "react";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "../ui/select";
import { Users } from "lucide-react";

function CreateGame() {
  const [playerCount, setPlayerCount] = useState("2");
  // const [timeLimit, setTimeLimit] = useState("0");
  // const [privateGame, setPrivateGame] = useState(false);

  useEffect(() => {
    // @ts-ignore
    window.Telegram.WebApp.BackButton.show();
    // @ts-ignore
    window.Telegram.WebApp.BackButton.onClick(() => {
      window.location.href = "/";
      // @ts-ignore
      window.Telegram.WebApp.BackButton.hide();
      return true;
    });
  }, []);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-green-100 p-4">
      <div className="w-full max-w-md overflow-hidden rounded-lg bg-white shadow-xl">
        <div className="relative bg-red-600 p-4 text-center">
          <h1 className="text-2xl font-bold tracking-wider text-white">
            NEW GAME
          </h1>
        </div>

        <form className="space-y-6 p-6">
          <div className="space-y-2">
            <Label htmlFor="player-count" className="flex items-center text-lg">
              <Users className="mr-2 h-5 w-5" />
              Number of Players
            </Label>
            <Select value={playerCount} onValueChange={setPlayerCount}>
              <SelectTrigger id="player-count">
                <SelectValue placeholder="Select player count" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="2">2 Players</SelectItem>
                <SelectItem value="3">3 Players</SelectItem>
                <SelectItem value="4">4 Players</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {/* <div className="space-y-2">
            <Label
              htmlFor="initial-money"
              className="text-lg flex items-center"
            >
              <DollarSign className="mr-2 h-5 w-5" />
              Initial Money
            </Label>
            <Input
              id="initial-money"
              type="number"
              placeholder="1500"
              defaultValue="1500"
            />
          </div> */}

          {/* <div className="space-y-2">
            <Label htmlFor="time-limit" className="text-lg flex items-center">
              <Timer className="mr-2 h-5 w-5" />
              Time Limit (minutes)
            </Label>
            <Select value={timeLimit} onValueChange={setTimeLimit}>
              <SelectTrigger id="time-limit">
                <SelectValue placeholder="Select time limit" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">No Limit</SelectItem>
                <SelectItem value="30">30 Minutes</SelectItem>
                <SelectItem value="60">60 Minutes</SelectItem>
                <SelectItem value="90">90 Minutes</SelectItem>
              </SelectContent>
            </Select>
          </div> */}

          {/* <div className="flex items-center space-x-2">
            <Switch id="use-ai" checked={useAI} onCheckedChange={setUseAI} />
            <Label htmlFor="use-ai" className="text-lg flex items-center">
              Use AI Players
            </Label>
          </div> */}

          {/* <div className="space-y-2">
            <Label htmlFor="board-theme" className="text-lg flex items-center">
              <MapPin className="mr-2 h-5 w-5" />
              Board Theme
            </Label>
            <Select defaultValue="classic">
              <SelectTrigger id="board-theme">
                <SelectValue placeholder="Select board theme" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="classic">Classic</SelectItem>
                <SelectItem value="city">City Edition</SelectItem>
                <SelectItem value="world">World Edition</SelectItem>
              </SelectContent>
            </Select>
          </div> */}

          {/* <div className="flex items-center space-x-2">
            <Switch
              id="privateGame"
              checked={privateGame}
              onCheckedChange={setPrivateGame}
            />
            <Label htmlFor="privateGame" className="text-lg flex items-center">
              Private
            </Label>
          </div> */}

          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="default"
            onClick={(e) => {
              e.preventDefault();
              window.location.href = "/game/1";
            }}
          >
            Start Game
          </Button>
        </form>
      </div>
    </div>
  );
}

export default CreateGame;
