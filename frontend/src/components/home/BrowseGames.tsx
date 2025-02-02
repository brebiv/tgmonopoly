import { useAuth } from "@/hooks";
import LoadingScreen from "../LoadingScreen";
import Forbidden from "../Forbidden";
// import { useNavigate } from "@tanstack/react-router";
import GameList from "./game_list/GameList";
import { useTheme } from "@/stores/ThemeContext";

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
      className="flex min-h-screen flex-col items-center gap-40 p-4"
      style={{
        backgroundColor: secondaryBGColor,
        color: textColor,
      }}
    >
      <div>
        <h1>Welcome back!</h1>
      </div>
      <GameList />
    </div>
  );
}

export default BrowseGames;
