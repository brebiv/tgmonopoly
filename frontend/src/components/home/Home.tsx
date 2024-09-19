import { Button } from "../ui/button";
import { DollarSign, PlayCircle, Settings, Book, Globe } from "lucide-react";

function Home() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-green-100 p-4">
      <div className="w-full max-w-md overflow-hidden rounded-lg bg-white shadow-xl">
        <div className="bg-red-600 p-4 text-center">
          <h1 className="text-4xl font-bold tracking-wider text-white">
            MONOPOLY
          </h1>
        </div>

        <div className="space-y-6 p-6">
          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="default"
            onClick={() => (window.location.href = "/create_game")}
          >
            <PlayCircle className="mr-2 h-6 w-6" />
            New Game
          </Button>

          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="outline"
            disabled
          >
            <Globe className="mr-2 h-6 w-6" />
            Browse Games
          </Button>

          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="outline"
            disabled
          >
            <Settings className="mr-2 h-6 w-6" />
            Settings
          </Button>

          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="outline"
            disabled
          >
            <Book className="mr-2 h-6 w-6" />
            Rules
          </Button>
        </div>

        <div className="flex items-center justify-center bg-green-600 p-4">
          <DollarSign className="h-12 w-12 text-yellow-300" />
        </div>
      </div>
    </div>
  );
}

export default Home;
