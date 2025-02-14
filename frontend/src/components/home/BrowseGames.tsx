import { useAuth } from "@/hooks";
import LoadingScreen from "../LoadingScreen";
import Forbidden from "../Forbidden";
// import { useNavigate } from "@tanstack/react-router";
import GameList from "./game_list/GameList";
import { useTheme } from "@/stores/ThemeContext";
import CurrentGame from "./game_list/CurrentGame";
import HomeBanner from "./HomeBanner";

function BrowseGames() {
  const { data: me, isLoading: isMeLoading, isError: isMeError } = useAuth(true);
  const { textColor, secondaryBGColor } = useTheme();

  // const navigate = useNavigate();

  if (isMeError) {
    return <Forbidden />;
  }

  if (me == undefined || isMeLoading) {
    return <LoadingScreen />;
  }

  return (
    <div
      className="flex min-h-screen flex-col items-center gap-4 px-4 py-2 pb-4"
      style={{
        backgroundColor: secondaryBGColor,
        color: textColor,
      }}
    >
      <HomeBanner />
      {me.current_game_link ? <CurrentGame /> : <GameList />}
    </div>
  );
}

export default BrowseGames;
