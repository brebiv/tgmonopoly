import { Button } from "../ui/button";
import { DollarSign, PlayCircle, Settings, Book, Globe } from "lucide-react";
import { useAuth } from "@/hooks";
import LoadingScreen from "../LoadingScreen";
import Forbidden from "../Forbidden";
import { joinGame } from "@/api";

function Home() {
  const { data: me, isLoading: isMeLoading, isError: isMeError } = useAuth(true);

  if (isMeError) {
    return <Forbidden />;
  }

  if (me == undefined || isMeLoading) {
    return <LoadingScreen />;
  }

  return (
    <div
      className="flex min-h-screen flex-col items-center justify-center p-4"
      style={{
        backgroundColor:
          // @ts-ignore
          window.Telegram.WebApp.themeParams.secondary_bg_color || "#334155",
      }}
    >
      <div className="w-full max-w-md overflow-hidden rounded-lg bg-white shadow-xl">
        <div
          className="bg-red-600 p-4 text-center"
          style={{
            backgroundColor:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.bottom_bar_bg_color || "#334155",
          }}
        >
          <h1 className="text-4xl font-bold tracking-wider text-white">MONOPOLY</h1>
        </div>

        <div
          className="space-y-6 p-6"
          style={{
            backgroundColor:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.bg_color || "#334155",
          }}
        >
          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="default"
            onClick={() => {
              window.location.href = "/create_game";
            }}
            style={{
              backgroundColor:
                // @ts-ignore
                window.Telegram.WebApp.themeParams.button_color || "",
              color:
                // @ts-ignore
                window.Telegram.WebApp.themeParams.button_text_color || "",
            }}
          >
            <PlayCircle className="mr-2 h-6 w-6" />
            New Game
          </Button>
          <Button
            className="w-full py-6 text-lg font-semibold"
            variant="outline"
            onClick={async () => {
              let resp = await joinGame("random-uuid");
              if (resp.status === "ok") {
                window.location.href = resp.next_url;
              }
            }}
          >
            <Globe className="mr-2 h-6 w-6" />
            Browse Games
          </Button>
          <Button className="w-full py-6 text-lg font-semibold" variant="outline" disabled>
            <Settings className="mr-2 h-6 w-6" />
            Settings
          </Button>
          <Button className="w-full py-6 text-lg font-semibold" variant="outline" disabled>
            <Book className="mr-2 h-6 w-6" />
            Rules
          </Button>
        </div>

        <div
          className="flex items-center justify-center bg-green-600 p-4"
          style={{
            backgroundColor:
              // @ts-ignore
              window.Telegram.WebApp.themeParams.bottom_bar_bg_color || "#334155",
          }}
        >
          <DollarSign className="h-12 w-12 text-yellow-300" />
        </div>
      </div>
    </div>
  );
}

export default Home;
