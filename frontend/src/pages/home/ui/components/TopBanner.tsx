import { useAuthContext } from "@/entities/AuthProvider";
import { CurrentGameCard } from "./CurrentGameCard";
import { DailyReward } from "./DailyReward";

type States = "current_game" | "home";

export const TopBaner = () => {
  const { me } = useAuthContext();
  let state: States;

  if (me.current_game) {
    state = "current_game";
  } else {
    state = "home";
  }

  return (
    <div>
      {state === "current_game" && <CurrentGameCard game={me.current_game!} />}
      {state === "home" && <DailyReward />}
    </div>
  );
};
