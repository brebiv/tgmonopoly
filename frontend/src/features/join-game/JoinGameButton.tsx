import { joinGame } from "@/shared/api";
import { Button } from "@/shared/ui/Button";
import { navigateToGame } from "@/shared/utils";
import type React from "react";
// import { motion } from "motion/react";

interface JoinGameButtonProps {
  gameUUID: string;
  text?: string;
}

export const JoinGameButton: React.FC<JoinGameButtonProps> = ({ gameUUID, text = "Join" }) => {
  return (
    <Button
      onClick={async () => {
        const resp_data = await joinGame(gameUUID);
        navigateToGame(resp_data.game_uuid);
      }}
      className="relative overflow-hidden rounded-xl p-3"
      // className="overflow-hidden rounded-xl p-3"
    >
      <p className="text-button-text w-12 text-lg">{text}</p>
      {/* <motion.div
        initial={{ bottom: "-100%", left: "-100%" }}
        animate={{ bottom: "100%", left: "100%" }}
        transition={{ duration: 1 }}
        className={`absolute h-[120%] w-[120%] rotate-45`}
        style={{
          background:
            "linear-gradient(to bottom, rgba(229, 172, 142, 0), rgba(255,255,255,0.5) 50%, rgba(229, 172, 142, 0))",
          // bottom: "-100%",
          // left: "-100%",
        }}
      ></motion.div> */}
    </Button>
  );
};
